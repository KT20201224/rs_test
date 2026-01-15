# Restaurant LLM Evaluation System

A comprehensive framework for comparing LLM performance on restaurant recommendation tasks.

## 📋 Features

- **Unified Interface**: Seamless support for OpenAI, Gemini, and Local HuggingFace models.
- **Domain-Specific Testing**: 
  - Persona Generation (Structured JSON extraction)
  - Persona Rating (Reasoning alignment)
  - Menu Recommendation (Constraint satisfaction)
- **Auto-Evaluation**: Custom metrics for JSON validity, safety, and reasoning quality.
- **Cost & Performance Tracking**: Detailed logs of latency, tokens, and approximate USD cost.
- **Reporting**: Generates Markdown reports and raw JSON data.

## 🚀 Installation

1. **Clone the repository** (if applicable) or navigate to root.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Setup**:
   Create a `.env` file in the root:
   ```bash
   OPENAI_API_KEY=sk-...
   GOOGLE_API_KEY=...
   ```

## 💻 Usage

Run the evaluation via command line:

```bash
# Evaluate specific models
python main.py --models gpt-4o-mini --output results/run1

# Evaluate all configured models (including local if installed)
python main.py --models all

# Help
python main.py --help
```

## 📊 Results Interpretation

Reports are generated in the specified output directory:

- `report_YYYYMMDD_HHMMSS.md`: Human-readable summary.
  - **Overall Ranking**: Weighted score across tasks.
  - **Cost Analysis**: Cost per 1k tokens or task.
  - **Recommendations**: Best value vs. Best performance.
- `raw_results_....json`: Full trace for debugging.

## 📂 Project Structure

- `models/`: API and Local model wrappers.
- `evaluation/`: Test cases and metric logic.
- `utils/`: Helpers for cost tracking and reporting.
- `main.py`: Entry point.

## ⚠️ Notes for Local Models
- Local models (e.g., Qwen, Gemma) require `torch` and significant RAM/VRAM.
- The system defaults to CPU if CUDA is unavailable, which will vary slow.
