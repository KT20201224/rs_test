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
        with open(raw_path, 'w', encoding='utf-8') as f:
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
        
        # 2.1 구조화된 출력 생성 능력
        md += "#### 1. 구조화된 출력 생성 능력\n"
        md += "- JSON 형식 데이터 생성 정확도 및 필수 필드 누락 여부 평가\n"
        if not results_df.empty:
            # Parsing Error Rate = 1 - json_validity
            # Field Completeness
            struct_cols = ["json_validity", "field_completeness"]
            struct_cols = [c for c in struct_cols if c in results_df.columns]
            
            if struct_cols:
                struct_perf = results_df.groupby("model")[struct_cols].mean()
                # Calculate Parsing Error Rate
                if "json_validity" in struct_perf.columns:
                    struct_perf["parsing_error_rate"] = 1.0 - struct_perf["json_validity"]
                    
                md += struct_perf.to_markdown(floatfmt=".4f") + "\n\n"
            else:
                 md += "관련 메트릭 데이터 없음.\n\n"
        else:
            md += "데이터 없음.\n\n"

        # 2.2 일관성
        md += "#### 2. 일관성\n"
        md += "- 같은 입력에 대해 여러 번 실행했을 때의 일관성 (Temperature=0, 3회 반복 측정)\n"
        if "consistency" in results_df.columns:
            consistency_perf = results_df.groupby("model")[["consistency"]].mean()
            md += consistency_perf.to_markdown(floatfmt=".4f") + "\n\n"
        else:
             md += "일관성 데이터 없음.\n\n"
             
        # 2.3 추론 품질
        md += "#### 3. 추론 품질\n"
        md += "- 페르소나 특성 반영 및 CoT 추론 과정 평가\n"
        # Combine reasoning quality metrics
        reasoning_cols = ["cot_quality", "reasoning_quality", "rating_appropriateness", "explanation_quality"]
        reasoning_cols = [c for c in reasoning_cols if c in results_df.columns]
        
        if reasoning_cols:
             reasoning_perf = results_df.groupby("model")[reasoning_cols].mean()
             md += reasoning_perf.to_markdown(floatfmt=".4f") + "\n\n"
        else:
             md += "추론 품질 데이터 없음.\n\n"

        # --- 3. 실용적 제약사항 ---
        md += "### 3. 실용적 제약사항\n"
        
        if not cost_df.empty:
            # 3.1 응답 속도
            md += "#### 1. 응답 속도(Latency)\n"
            latency_stats = cost_df.groupby("model")["latency_ms"].agg(['mean']).rename(columns={'mean': 'avg_latency_ms'})
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
                     pricing_str = f"In:${pricing.get('input')}/Out:${pricing.get('output')}"
                else:
                     pricing_str = str(pricing)
                
                cost_data.append({
                    "model": m,
                    "avg_cost_per_req": avg_cost_req,
                    "monthly_projection(10k)": monthly,
                    "token_price_1M": pricing_str,
                    "io_token_ratio_input_output": io_ratio
                })
                
            cost_summary_df = pd.DataFrame(cost_data).set_index("model")
            md += cost_summary_df.to_markdown(floatfmt=".6f") + "\n\n"
            
        else:
            md += "비용 데이터 없음.\n\n"

        
        report_path = os.path.join(self.results_dir, f"report_{timestamp}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md)
            
        print(f"Reports generated: \n - {raw_path}\n - {report_path}")
