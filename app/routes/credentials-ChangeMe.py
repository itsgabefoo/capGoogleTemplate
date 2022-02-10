import os

# After you change the variables below, change the name of the file to be credentials.py.  This 
# file is blocked from syncing to github via the gitignore file.  DO NOT change that! It will give people access to 
# your google client account.

GOOGLE_CLIENT_CONFIG = {
    "web":{
        "client_id":"<your client ID goes here>",
        "project_id":"<Name of your project at Google Cloud>",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":"<client secret from google>",
        "redirect_uris":
            [
                "https://127.0.0.1:5000/oauth2callback",
                "https://localhost:5000/oauth2callback"
            ]
        }
}