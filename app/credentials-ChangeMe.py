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

#This is the name of the database you are connecting to at mongoDB
mongo_db_name = "<mongoDB data base name>"
#This is the connect string that you copied when you configured your database
#Be sue to put the db admin name and the password you created when you made your mongodb
#account.  This is NOT the name and pw that you use to login to MongoDB but it is the user
#that you created to administer the database. Take a look at the example below.  The cluster 
#part will be different for your database.
mongo_host = "mongodb+srv://<admin_user>:<pw_for_Admin_User>@cluster0.8m0v1.mongodb.net/<database_name>?retryWrites=true&w=majority"
