# Job search app

A Streamlit interface for searching Google Jobs through SerpApi.

## Run locally

1. Install the dependencies with `python -m pip install -r requirements.txt`.
2. Set your SerpApi key in the `SERPAPI_KEY` environment variable, or enter it in the app's sidebar.
3. Start the app with `streamlit run main.py`.

The app sends search filters to SerpApi only when you submit the form. API keys are not stored in the source code or printed in logs.

## Remote debugging with local browser profile

Turn on remote debugging in your browser:
chrome://inspect/#remote-debugging

Copy your browser profile somewhere else, locally:

cp -r /c/Users/andre/AppData/Local/Google/Chrome/User\ Data/Default .PlayWrightProfiles/

Then start remote debugging port, example if you use chrome:

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\<YOUR_SYSTEM_USER>\AppData\Local\Google\Chrome\User Data" --profile-directory=<Default OR Your custom browser profile name>

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\andre\AppData\Local\Google\Chrome\User Data" --profile-directory=Default