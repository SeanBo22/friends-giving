# Friendsgiving Invite

A simple Streamlit app for a Friendsgiving invite and signup sheet.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

http://localhost:8501

## Share it with others

The easiest way is to deploy it to Streamlit Community Cloud:

1. Push this folder to a GitHub repository.
2. Go to https://share.streamlit.io
3. Select the repo and choose `app.py`.
4. Deploy.
5. Share the generated link with your friends.

## Notes

- RSVPs are saved to `friendsgiving_signups.csv` in the project folder.
- For a more permanent setup, you can connect the app to Google Sheets or Airtable instead of storing the file locally.
