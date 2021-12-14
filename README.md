# FreeMarket
#### Video Demo: https://youtu.be/QSB6-QtohV4
#### Description:
This project is a generic clone of sites like: Amazon, olx, ebay and several other marketplaces.
 
## How to setup
- The entire backend of this application was created using the framework (Flask)
- To run the project, change the global variable FLASK APP, typing:
```
   export FLASH_APP=application
```
- And then
```
   flask run
```
- The application will inform the port that the program will be served.
- The page will be served on port 5000 by default. Therefore, just access, through a browser of your choice, the url localhost:5000.
## Features
 
Register (register.html)
- To create a new account just select the register option and select a username and password (avoid choosing a real password).
 
Login (login.html)
- If your account exists, just fill in the form with username and password.
 
Post (post.html)
- To create a new post you must be logged in.
- By selecting the My Posts option you have access to all your posts in addition to the New Post option.
- To post you need to select the desired image, a title, price and description
 
View (index.html / more.html)
- On the home page you have access to all products/services available on the site.
- Selecting the Search field you can search by product titles.
- Clicking on a product takes you to a product page.
