# Instagram-clone-with-FLASK
A FullStack Instagram App built with Flask and React. 
<p id ="top" align="center">
  <img src="https://i.ibb.co/F3Vq9SD/login-page.png" width="45%" height="auto">
</p>

Checkout the site in action here <a href="https://yash-marmat-projects-instagram.netlify.app/">Deployed App</a>

# Table of contents
- [Technologies_and_Tech_stack_involved](#Technologies_and_Tech_stack_involved)
- [About_this_App](#About_this_App)
  * [Home_page](#Home_page)
  * [Single_post_page](#Single_post_page)
  * [Add_Comment](#Add_Comment)
  * [Explore_Page](#Explore_Page)
  * [User_Inbox](#User_Inbox)
  * [Your_Profile_Page](#Your_Profile_Page)
  * [Login_Page](#Login_Page)
  * [Sign_up_page](#Sign_up_page)
  * [Short_Note](#Short_Note)
- [Installation](#Installation)
  * [Backend](#backend)


## Technologies_and_Tech_stack_involved
- Python
- Javascript
- light weight sqlite database
- React
- Redux
- Flask
- JWT (token authentication)

## About_this_App
- An Instagram clone build with Flask, React, Redux.  
- Allows users to like, share, comment, posts or create their own. 
- follow or get connected with other users and more functionalities within the app to discover.

### Home_page
This page displays posts of only those users whom you are following.
<p align="center">
  <img src="https://i.ibb.co/xqsCmZK/insta-homepage.png" width="50%" height="auto">
</p>

### Single_post_page
This page displays the complete details about the post (like about, liked by, comments etc.)
<p align="center">
  <img width="400px" height="400px" src="https://github.com/YashMarmat/Pages-App-django/blob/master/templates/ecommerce%20%20product%20details%20page.png?raw=true">
</p>

### Add_Comment
The application is little strict about comments 😁, you need to follow the post's author in order to add comments (you can remove this feature too from the code).
<p align="center">
  <img src="https://github.com/YashMarmat/Pages-App-django/blob/master/templates/ecommerce%20%20product%20edit%20page.png?raw=true" width="100%">
</p>

### Explore_Page
At this page you can see posts, made by all the signed up users in the application (global posts in short).
<p align="center">
  <img src="https://github.com/YashMarmat/Pages-App-django/blob/master/templates/ecommerce%20%20add%20product%20page.png?raw=true" width="100%">
</p>

### User_Inbox
Just like istagram here you can see your messages (your inbox basically), you can also send a new message to any user present in the application.
<p align="center">
  <img src="https://github.com/YashMarmat/Pages-App-django/blob/master/templates/ecommerce%20%20checkout%20page.png?raw=true" width="100%">
</p>

### Your_Profile_Page
Here you can manage your profile information like your profile picture (which you can update), your posts, followers and the people you are following.
Also, just like instagram can also visit other peoples profile as well.
<p align="center">
  <img src="https://github.com/YashMarmat/Pages-App-django/blob/master/templates/ecommerce%20%20payment%20confirmation%20page.png?raw=true" width="100%">
</p>

### Login_Page
<p align="center">
  <img src="https://github.com/YashMarmat/Pages-App-django/blob/master/templates/ecommerce%20%20payment%20confirmation%20page.png?raw=true" width="100%">
</p>

### Sign_up_page
<p align="center">
  <img src="https://github.com/YashMarmat/Pages-App-django/blob/master/templates/ecommerce%20%20payment%20confirmation%20page.png?raw=true" width="100%">
</p>

## Short_Note
For this application i have only made available the apis or backend part, so that you can feel free to design your own UI based on any frontend library or framework of your choice. You can also test the apis with postman (shared below)  

## Installation
after downloading/cloning the repository code, follow below steps:

### Backend

- create your virtual environment
`python -m venv myenv` 

- activate your virtual environment
`myenv\scripts\activate`

- install project dependencies
`pip install -r requirements.txt`

- create your flask database
`flask db init`

- make your first migration
`flask db migrate -m "create tables"`

- upgrade or update your database
flask db upgrade

- run the project
`flask run`


## All set ! Happy coding :)

<p><a href="#top">Back to Top</a></p>

