import os

GOOGLE_CLIENT_CONFIG = {
    "web":{
        "client_id":"156309448916-0glcf34pe18fdl2cgb84796i0b6svk2m.apps.googleusercontent.com",
        "project_id":"CapstoneTemplate",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":"8pZCtCL_c35o9HOtw2MeOp5A",
        "redirect_uris":
            [
                "https://127.0.0.1:5000/oauth2callback",
                "https://localhost:5000/oauth2callback"
            ]
        }
}

#connect("capGoogleTemplate", host='mongodb+srv://capGoogleTemplate:bu11dogz@cluster0.8m0v1.mongodb.net/capGoogleTemplate?retryWrites=true&w=majority')
