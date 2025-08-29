# Echo v62 — Local Runner (PLUS Panels)

This is a local, privacy-first implementation of your Echo system with **extra Streamlit panels**:
- Loan Heat Map
- Catalyst Countdown
- Risk/Reward Heatmap
- Sector Flow Scanner

## Quick start
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run echo/app_streamlit.py
```

Or generate a terminal report:
```bash
python -m echo.main --report daily
```

Edit `echo/config.yaml` to match your plan.


## AI Copilot Setup
- Open `docs/AI_COPILOT_README.md` and paste the **Short Project Brief** into your copilot's workspace instructions.
- Keep this repo open in your editor so the copilot can read files.
