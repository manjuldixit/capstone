# ai-banking-advisory-agent Streamlit Frontend

This folder contains the Streamlit UI for the ai-banking-advisory-agent Equipment Financing Agent.

## Run the frontend

1. Start the backend API from `capstone/ai-banking-advisory-agent/backend`:

```powershell
cd capstone/ai-banking-advisory-agent/backend
python deploy_server.py
```

2. Run the Streamlit app from `capstone/ai-banking-advisory-agent`:

```powershell
cd capstone/ai-banking-advisory-agent
streamlit run frontend/app.py
```

## What it does

- sends user questions to the deployed backend API
- displays agent responses with metadata
- allows feedback submission for adaptive behavior
- shows session state and adaptation summary

## Dependencies

Install dependencies with:

```powershell
pip install -r frontend/requirements.txt
```

