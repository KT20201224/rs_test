import json
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict
from config import MODEL_PRICING


class ReportGenerator:
    def __init__(self, results_dir: str):
        self.results_dir = results_dir

    def generate_report(self, run_results: List[Dict], cost_df: pd.DataFrame):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Save Raw JSON
        raw_path = os.path.join(self.results_dir, f"raw_results_{timestamp}.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(run_results, f, ensure_ascii=False, indent=2)

        # 2. Process Data for Analysis
        flattened_data = []
        for r in run_results:
            row = r.get("metrics", {}).copy()
            row["model"] = r["model"]
            row["task"] = r["task"]
            row["success"] = r["success"]
            # Flatten some nested metrics if needed, but current metrics are flat
            flattened_data.append(row)

        results_df = pd.DataFrame(flattened_data)

        # 3. Generate Markdown Report (User Requested Format)
        md = f"# LLM 모델 평가 리포트 📊\n\n**생성 일시**: {timestamp}\n\n"

        # --- 2. 태스크 특화 평가 ---
        md += "### 2. 태스크 특화 평가\n"

        # --- 2. 상세 품질 평가 (Advanced Metrics) ---
        md += "### 2. 품질 상세 평가 (Quality Metrics)\n\n"

        # 2.1 기본 구조 건전성
        md += "#### 1. 기본 구조 건전성 (Structural Health)\n"
        md += "- **Parsing Error Rate**: JSON 파싱 실패 비율 (낮을수록 좋음)\n"
        md += "- **Field Completeness**: 필수 필드(이름, 나이, 분석 등)가 모두 존재하는지 (1.0 = 완벽)\n"
        md += "- **Schema Compliance**: 데이터 타입(리스트, 문자열 등) 준수 여부 (1.0 = 준수)\n\n"

        struct_cols = [
            "json_validity",
            "field_completeness",
            "schema_compliance",
            "value_accuracy",
        ]
        struct_cols = [c for c in struct_cols if c in results_df.columns]

        if struct_cols:
            struct_perf = results_df.groupby("model")[struct_cols].mean()
            if "json_validity" in struct_perf.columns:
                struct_perf["parsing_error_rate"] = 1.0 - struct_perf["json_validity"]
            md += struct_perf.to_markdown(floatfmt=".4f") + "\n\n"

        # 2.2 페르소나 생성 품질 (핵심 지표)
        md += "#### 2. 페르소나 생성 품질 (Persona Quality - 핵심)\n"
        md += "**이 섹션은 모델이 얼마나 '사람 같은' 페르소나를 만들었는지 평가합니다.**\n\n"
        md += "- **CoT Depth Score (추론 깊이)**: 단순 데이터 나열이 아닌, '왜' 그런 취향을 가졌는지에 대한 논리적 연결 깊이 (0.0~1.0). (높을수록 좋음)\n"
        md += "- **Persona Specificity (구체성)**: 페르소나가 구체적인 상황(주말, 퇴근, 데이트 등), 감정, 라이프스타일 맥락을 포함하는지 (0.0~1.0). (높을수록 좋음)\n"
        md += "- **Safety Consistency (안전성/일관성)**: 입력된 알러지 정보를 누락하거나 모순된 식습관(알러지 재료 선호 등)을 생성하지 않았는지 (1.0 = 안전). (매우 중요)\n\n"

        quality_cols = ["cot_depth_score", "persona_specificity", "safety_consistency"]
        quality_cols = [c for c in quality_cols if c in results_df.columns]

        if quality_cols:
            quality_perf = results_df.groupby("model")[quality_cols].mean()
            md += quality_perf.to_markdown(floatfmt=".4f") + "\n\n"

        # 2.3 일관성
        md += "#### 3. 생성 일관성 (Consistency)\n"
        md += "- **Consistency**: 같은 입력에 대해 여러 번 실행했을 때 주요 속성(이름, 알러지 등)이 유지되는지 (1.0 = 완벽히 동일)\n"
        if "consistency" in results_df.columns:
            consistency_perf = results_df.groupby("model")[["consistency"]].mean()
            md += consistency_perf.to_markdown(floatfmt=".4f") + "\n\n"

        # --- 3. 실용적 제약사항 ---
        md += "### 3. 실용적 제약사항\n"

        if not cost_df.empty:
            # 3.1 응답 속도
            md += "#### 1. 응답 속도(Latency)\n"
            latency_stats = (
                cost_df.groupby("model")["latency_ms"]
                .agg(["mean"])
                .rename(columns={"mean": "avg_latency_ms"})
            )
            md += latency_stats.to_markdown(floatfmt=".2f") + "\n\n"

            # 3.2 Cost
            md += "#### 2. Cost\n"

            # Prepare Cost Table
            cost_data = []
            models = cost_df["model"].unique()

            for m in models:
                m_df = cost_df[cost_df["model"] == m]
                avg_cost_req = m_df["cost_usd"].mean()
                monthly = avg_cost_req * 10000

                total_input = m_df["input_tokens"].sum()
                total_output = m_df["output_tokens"].sum()

                if total_output > 0:
                    ratio_val = total_input / total_output
                    io_ratio = f"{ratio_val:.1f}:1"
                else:
                    io_ratio = "N/A"

                # Pricing Info
                pricing = MODEL_PRICING.get(m, "N/A")
                if isinstance(pricing, dict):
                    pricing_str = (
                        f"In:${pricing.get('input')}/Out:${pricing.get('output')}"
                    )
                else:
                    pricing_str = str(pricing)

                cost_data.append(
                    {
                        "model": m,
                        "avg_cost_per_req": avg_cost_req,
                        "monthly_projection(10k)": monthly,
                        "token_price_1M": pricing_str,
                        "io_token_ratio_input_output": io_ratio,
                    }
                )

            cost_summary_df = pd.DataFrame(cost_data).set_index("model")
            md += cost_summary_df.to_markdown(floatfmt=".6f") + "\n\n"

        else:
            md += "비용 데이터 없음.\n\n"

        report_path = os.path.join(self.results_dir, f"report_{timestamp}.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"Reports generated: \n - {raw_path}\n - {report_path}")
