import streamlit as st
import pandas as pd
import json
import os
import glob
from evaluation.evaluators import Evaluator
from config import API_MODELS, LOCAL_MODELS
from utils.report_generator import ReportGenerator
from utils.cost_tracker import CostTracker
from models.unified_interface import UnifiedLLMInterface

# Set page config
st.set_page_config(page_title="LLM Persona Evaluator", page_icon="🍽️", layout="wide")

# Title
st.title("🍽️ Restaurant LLM Persona Evaluator")
st.markdown("""
이 대시보드는 다양한 LLM 모델이 **'사용자 페르소나'**를 얼마나 잘 생성하는지 정량적/정성적으로 평가합니다.
""")

# Sidebar: Model Selection
st.sidebar.header("Model Selection")

st.sidebar.subheader("API Models")
selected_api_models = st.sidebar.multiselect(
    "OpenAI / Others", options=list(API_MODELS.keys()), default=list(API_MODELS.keys())
)

st.sidebar.subheader("Local Models (GPU)")
selected_local_models = st.sidebar.multiselect(
    "HuggingFace Models",
    options=list(LOCAL_MODELS.keys()),
    default=[],  # Default to empty to avoid heavy load by mistake
)

selected_model_names = selected_api_models + selected_local_models

# Run Button
if st.sidebar.button("🚀 Run Evaluation", type="primary"):
    if not selected_model_names:
        st.error("Please select at least one model.")
    else:
        with st.spinner(
            f"Evaluating models: {', '.join(selected_model_names)}... This may take a while."
        ):
            try:
                # 0. Instantiate Models
                loaded_models = []
                for name in selected_model_names:
                    loaded_models.append(UnifiedLLMInterface(name))

                # 1. Run Evaluation
                cost_tracker = CostTracker()
                evaluator = Evaluator(loaded_models, cost_tracker)
                run_results = evaluator.run_all()

                # 2. Add to session state
                st.session_state["run_results"] = run_results
                st.session_state["last_run_models"] = selected_model_names

                # 3. Generate Report to get stats
                # We can reuse ReportGenerator logic or process manually
                # Let's save results temporarily to leverage existing logic
                if not os.path.exists("./results"):
                    os.makedirs("./results")

                # Find latest report
                list_of_files = glob.glob("./results/report_*.md")
                if list_of_files:
                    latest_file = max(list_of_files, key=os.path.getctime)
                    with open(latest_file, "r") as f:
                        st.session_state["latest_report"] = f.read()

                st.success("Evaluation Complete!")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Display Results
if "run_results" in st.session_state:
    results = st.session_state["run_results"]

    # Process results into DataFrame for charts
    rows = []
    for r in results:
        m = r.get("metrics", {})
        m["model"] = r["model"]
        m["generated_text"] = r.get("output", {}).get("content", "")
        m["input_prompt"] = r.get("input", {}).get("prompt", "")
        # Add persona details if available
        try:
            content_json = json.loads(m["generated_text"])
            m["persona_name"] = content_json.get("name", "Unknown")
        except:
            m["persona_name"] = "Parse Error"
        rows.append(m)

    df = pd.DataFrame(rows)

    # Tabs
    tab1, tab2, tab3 = st.tabs(
        ["📊 Metrics Comparison", "📝 Generated Personas", "📑 Full Report"]
    )

    with tab1:
        st.subheader("Model Performance Metrics")

        # Key Metrics
        metrics_to_show = [
            "cot_depth_score",
            "persona_specificity",
            "safety_consistency",
            "json_validity",
        ]
        available_metrics = [m for m in metrics_to_show if m in df.columns]

        if available_metrics:
            # Group by model
            perf_df = df.groupby("model")[available_metrics].mean()
            st.dataframe(perf_df.style.highlight_max(axis=0), use_container_width=True)

            # Charts
            st.bar_chart(perf_df)
        else:
            st.warning("No metrics available to plot.")

    with tab2:
        st.subheader("Inspect Generated Outputs")

        # Filter by Model
        model_filter = st.selectbox("Select Model to Inspect", df["model"].unique())
        if model_filter:
            filtered_df = df[df["model"] == model_filter]

            # Show each generation
            for idx, row in filtered_df.iterrows():
                with st.expander(
                    f"Persona: {row['persona_name']} (Metrics: Depth={row.get('cot_depth_score', 0):.2f}, Spec={row.get('persona_specificity', 0):.2f})"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Generated JSON:**")
                        st.json(row["generated_text"])
                    with col2:
                        st.markdown("**Analysis:**")
                        st.write(
                            f"- **Safety**: {row.get('safety_consistency', 'N/A')}"
                        )
                        st.write(f"- **JSON Valid**: {row.get('json_validity', 'N/A')}")
                        st.markdown("---")
                        st.caption("Raw output content")

    with tab3:
        if "latest_report" in st.session_state:
            st.markdown(st.session_state["latest_report"])
        else:
            st.info("No report generated yet.")
else:
    st.info("Select models from the sidebar and click 'Run Evaluation' to start.")
