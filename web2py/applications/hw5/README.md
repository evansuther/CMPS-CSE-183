This project is designed to work in Web2Py, a python program for running a webserver.
___
The goal of this project was to create a mock shopping website with a list of products, reviews for products(both text and stars) and a shopping cart per user.
___
The files I was responsible for in this project(Web2Py gives you starter code for a web application) were static/JS/default_index.js, static/css/custom.css, static/css/myapp.css, views/default/index.html, controllers/api.py, controllers/default.py, models/tables.py.

### default_index.js
At the high level default_index.js was responsible for fetching the products, reviews and user cart using Jquery.js to query the api.py and storing them in Javascript variables. Using Vue.js, this information was then added to the HTML view after receiving a response from the server.
I also implemented a search function which simply changed the displayed products based on what search term was in the search bar.

### custom.css and myapp.css
These two files were responsible for styling the HTML.

### api.py
api.py was responsible for serving or updating database information to the the Javascript. A request would come in, and using variables in the request, api.py performs a 
database query. Most responses from api.py were in the from of JSON.

### default.py
This is to fit into Web2Py's web app development pipeline. Default.py defines which pages are viewable in the web app.

### tables.py
tables.py defines the various database tables used throughout the project. The tables are implemented in Web2Py's database abstraction layer which is a pythonic way to interact with MySQL.

