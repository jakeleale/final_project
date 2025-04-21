# Final Project: Spotify Playlist Generator
By Jake Leale

Description: A tool that uses the Spotify's API to allow a user to make a playlist using their Liked Songs library, favorite songs, and songs from their favorite artists. 

## API Setup
To get started we must get access to Spotify's API. To do this we will visit the website https://developer.spotify.com/ and go to the dashboard. 
From there you will hit the create app button, and create the app that will give you a client id and client secret. 

<img width="1395" alt="Screen Shot 2025-04-20 at 9 37 16 PM" src="https://github.com/user-attachments/assets/9a08f55c-5709-4ea2-8184-e846df35e5c8" />
This is the dashboard for the Spotify developers app. You want to click the blue button of create app. 

<img width="1398" alt="Screen Shot 2025-04-20 at 9 37 41 PM" src="https://github.com/user-attachments/assets/5e8294d8-2a60-40e1-9a2a-2a34e009c74e" />
Once your app is created, you will see the client secret and client id. I have blocked mine out to keep the integrity of the application. These will give you access to Spotify's API within the backend of the project.

## Pythonanywhere Setup
This project uses the website https://www.pythonanywhere.com/ to hold both its backend and frontend components. It is completely free and allows easy creation of a public domain. First, create an account or login to your current account. Next create a web app, you should be ready to go after downloading the files needed on this github repository. 

## Directory Set up 
After downloading the files, upload the flask_app.py into the /mysite folder. This should be located in the files tab. 
Next, create a folder within the /mysite directory, label it templates. From there place the remaining frontend files in this templates folder. This will not work if the directory is any different. 

<img width="1404" alt="Screen Shot 2025-04-20 at 9 39 21 PM" src="https://github.com/user-attachments/assets/986dba1d-468b-465f-b23e-8042f7386f3b" />
This is within the /mysite directory. Notice the template folder created by the add folder button.

<img width="1401" alt="Screen Shot 2025-04-20 at 9 39 40 PM" src="https://github.com/user-attachments/assets/d82bdb25-0c5e-4bcd-a8df-03b1ab246a73" />
This is within the folder templates. It should look like this

## Credential Replacements
Once everything is setup, replace 
