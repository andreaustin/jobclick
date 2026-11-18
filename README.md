# Job search app

A Streamlit interface for searching Google Jobs through SerpApi.

## Run locally

1. Install the dependencies with `python -m pip install -r requirements.txt`.
2. Set your SerpApi key in the `SERPAPI_KEY` environment variable, or enter it in the app's sidebar.
3. Start the app with `streamlit run main.py`.

The app sends search filters to SerpApi only when you submit the form. API keys are not stored in the source code or printed in logs.
