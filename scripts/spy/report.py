#!/usr/bin/env python3
"""
性能分析报告生成工具

分析 py-spy 生成的性能数据，生成详细的性能报告

使用方法:
    python scripts/spy/report.py profile.svg
    python scripts/spy/report.py profile.svg --format html --output report.html
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path


class PerformanceReportGenerator:
    def __init__(self, profile_file: str):
        self.profile_file = Path(profile_file)
        self.data: dict[str, int] = defaultdict(int)
        self.load_data()

    def load_data(self):
        """加载性能数据"""
        if self.profile_file.suffix == ".svg":
            self._parse_svg()
        elif self.profile_file.suffix in {".json", ".raw"}:
            self._parse_json()
        else:
            print(f"不支持的文件格式: {self.profile_file}")
            sys.exit(1)

    def _parse_svg(self):
        """解析 SVG 火焰图文件"""
        try:
            import re
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                content = f.read()

            pattern = r'<g[^>]*>\s*<title>([^<]+)\s*\(\d+\s*samples[^<]*</title>'
            matches = re.findall(pattern, content)

            for func_name in matches:
                self.data[func_name.strip()] += 1

        except Exception as e:
            print(f"解析 SVG 文件时出错: {e}")
            sys.exit(1)

    def _parse_json(self):
        """解析 JSON 格式的性能数据"""
        try:
            with open(self.profile_file, 'r') as f:
                for line in f:
                    if '\t' in line:
                        parts = line.strip().split('\t')
                        if len(parts) >= 2:
                            func = parts[0]
                            count = int(parts[1])
                            self.data[func] += count
        except Exception as e:
            print(f"解析 JSON 文件时出错: {e}")
            sys.exit(1)

    def analyze(self) -> dict:
        """分析性能数据"""
        total = sum(self.data.values())
        sorted_data = sorted(self.data.items(), key=lambda x: x[1], reverse=True)

        analysis = {
            "total_samples": total,
            "unique_functions": len(self.data),
            "top_functions": [],
            "categories": defaultdict(int),
        }

        for func, count in sorted_data[:50]:
            percentage = (count / total * 100) if total > 0 else 0
            analysis["top_functions"].append({
                "function": func,
                "samples": count,
                "percentage": round(percentage, 2),
            })

            category = self._categorize_function(func)
            analysis["categories"][category] += count

        return analysis

    def _categorize_function(self, func: str) -> str:
        """分类函数"""
        func_lower = func.lower()

        if any(kw in func_lower for kw in ["await", "coroutine", "async"]):
            return "async_io"
        elif any(kw in func_lower for kw in ["sql", "query", "mysql", "select", "insert"]):
            return "database"
        elif any(kw in func_lower for kw in ["redis", "cache", "get", "set"]):
            return "cache"
        elif any(kw in func_lower for kw in ["uvicorn", "httptools", "request"]):
            return "http"
        elif any(kw in func_lower for kw in ["security", "jwt", "auth"]):
            return "security"
        elif any(kw in func_lower for kw in ["render", "template", "json"]):
            return "serialization"
        else:
            return "other"

    def generate_text_report(self) -> str:
        """生成文本格式报告"""
        analysis = self.analyze()

        lines = [
            "=" * 60,
            "性能分析报告",
            "=" * 60,
            f"总采样数: {analysis['total_samples']}",
            f"唯一函数数: {analysis['unique_functions']}",
            "",
            "-" * 60,
            "按类别分布:",
            "-" * 60,
        ]

        total = analysis["total_samples"]
        for category, count in sorted(analysis["categories"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"  {category:15s}: {count:8d} ({percentage:5.1f}%)")

        lines.extend([
            "",
            "-" * 60,
            "Top 20 热点函数:",
            "-" * 60,
        ])

        for i, func_data in enumerate(analysis["top_functions"][:20], 1):
            lines.append(
                f"{i:2d}. {func_data['function'][:40]:40s} "
                f"{func_data['samples']:8d} ({func_data['percentage']:5.1f}%)"
            )

        lines.extend([
            "",
            "=" * 60,
            "优化建议:",
            "=" * 60,
        ])

        lines.extend(self._generate_recommendations(analysis))

        return "\n".join(lines)

    def _generate_recommendations(self, analysis: dict) -> list[str]:
        """生成优化建议"""
        recommendations = []
        total = analysis["total_samples"]
        categories = analysis["categories"]

        if total == 0:
            return ["未收集到足够的性能数据"]

        for category, count in categories.items():
            percentage = (count / total * 100) if total > 0 else 0

            if category == "database" and percentage > 20:
                recommendations.extend([
                    f"数据库操作占用 {percentage:.1f}% CPU:",
                    "   - 检查是否有 N+1 查询问题",
                    "   - 考虑添加数据库连接池",
                    "   - 优化慢查询，添加必要的索引",
                ])
            elif category == "async_io" and percentage > 30:
                recommendations.extend([
                    f"异步操作占用 {percentage:.1f}% CPU:",
                    "   - 检查是否有阻塞性操作",
                    "   - 考虑使用更高效的异步库",
                ])
            elif category == "cache" and percentage > 15:
                recommendations.extend([
                    f"缓存操作占用 {percentage:.1f}% CPU:",
                    "   - 检查缓存命中率",
                    "   - 考虑使用本地缓存减少 Redis 访问",
                ])

        if not recommendations:
            recommendations.append("应用性能良好，未发现明显瓶颈")

        return recommendations

    def generate_html_report(self, output_file: str):
        """生成 HTML 格式报告"""
        analysis = self.analyze()

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>性能分析报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .chart-container {{
            margin: 20px 0;
        }}
        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .bar-item {{
            display: flex;
            align-items: center;
        }}
        .bar-label {{
            width: 120px;
            font-size: 14px;
            color: #333;
        }}
        .bar-track {{
            flex: 1;
            height: 25px;
            background: #eee;
            border-radius: 12px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: bold;
            font-size: 12px;
            transition: width 0.5s ease;
        }}
        .function-list {{
            margin-top: 20px;
        }}
        .function-item {{
            display: flex;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }}
        .function-item:hover {{
            background: #f8f9fa;
        }}
        .function-rank {{
            width: 30px;
            font-weight: bold;
            color: #667eea;
        }}
        .function-name {{
            flex: 1;
            font-family: monospace;
            color: #333;
        }}
        .function-stats {{
            text-align: right;
        }}
        .function-samples {{
            font-weight: bold;
            color: #333;
        }}
        .function-percent {{
            color: #666;
            font-size: 0.9em;
        }}
        .recommendations {{
            margin-top: 20px;
        }}
        .recommendation {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
        }}
        .recommendation.warning {{
            border-left-color: #ffc107;
            background: #fff8e1;
        }}
        .recommendation.success {{
            border-left-color: #28a745;
            background: #e8f5e9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>性能分析报告</h1>
            <p>分析文件: {self.profile_file.name}</p>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{analysis['total_samples']:,}</div>
                    <div class="stat-label">总采样数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{analysis['unique_functions']:,}</div>
                    <div class="stat-label">唯一函数数</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>类别分布</h2>
            <div class="chart-container">
                <div class="bar-chart">
"""

        total = analysis["total_samples"]
        for category, count in sorted(analysis["categories"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            width = percentage if percentage > 0 else 1
            html_content += f"""
                    <div class="bar-item">
                        <div class="bar-label">{category}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {width}%">{percentage:.1f}%</div>
                        </div>
                    </div>
"""

        html_content += """
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Top 20 热点函数</h2>
            <div class="function-list">
"""

        for i, func_data in enumerate(analysis["top_functions"][:20], 1):
            html_content += f"""
                <div class="function-item">
                    <div class="function-rank">{i}</div>
                    <div class="function-name">{func_data['function'][:60]}</div>
                    <div class="function-stats">
                        <div class="function-samples">{func_data['samples']:,}</div>
                        <div class="function-percent">{func_data['percentage']:.1f}%</div>
                    </div>
                </div>
"""

        html_content += """
            </div>
        </div>

        <div class="section">
            <h2>优化建议</h2>
            <div class="recommendations">
"""

        for rec in self._generate_recommendations(analysis):
            if "数据库" in rec:
                html_content += f'<div class="recommendation warning">{rec}</div>'
            elif "良好" in rec:
                html_content += f'<div class="recommendation success">{rec}</div>'
            else:
                html_content += f'<div class="recommendation">{rec}</div>'

        html_content += """
            </div>
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML 报告已生成: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="性能分析报告生成工具",
    )

    parser.add_argument(
        "profile_file",
        help="py-spy 生成的性能数据文件",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["text", "html"],
        default="text",
        help="输出格式 (默认: text)",
    )

    parser.add_argument(
        "--output", "-o",
        help="输出文件路径",
    )

    args = parser.parse_args()

    if not Path(args.profile_file).exists():
        print(f"错误: 文件不存在: {args.profile_file}")
        sys.exit(1)

    generator = PerformanceReportGenerator(args.profile_file)

    if args.format == "html":
        output_file = args.output or str(Path(args.profile_file).with_suffix(".html"))
        generator.generate_html_report(output_file)
    else:
        print(generator.generate_text_report())


if __name__ == "__main__":
    main()
