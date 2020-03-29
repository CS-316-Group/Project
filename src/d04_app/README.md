## RUNNING APP LOCALLY. THROUGH LOCAL HOST.
1. First step. Create a virtual environment through anaconda.
`conda create -n flask_app python=3.7.3`


2. Install all the dependencies in your application
`pip3 install -r requirements.txt`
(when is available)
dependencies is are all the pip libraries needed eg. flask, sqlalchemy. 
2a. To generate requirements.text run `pip freeze >> requirements.txt`
run this anytime you run a new library. 

3. Export Flask app.

`export FLASK_APP=app.py `
then `export FLASK_ENV=development`
and then `flask run` 
4.(might need to modify commands a little bit if computer is not MAC).



## General resources.

What are forms?

Web forms are one of the most basic building blocks in any web application. The Flask-WTF extension uses Python classes to represent web forms. A form class simply defines the fields of the form as class variables.

from forms to page templates.
The next step is to add the form to an HTML template so that it can be rendered on a web page.

useful pip commands.
1. `pip3 list` 
to show a list of packages installed. (this is specific to linus os might be different for mac os or windows os.



How to run the app.

1.there is an outdated version of this in
the vcm so if you are trying to run it from the vcm redownload the whole flask_app to the vcm through filezilla.

2.trying to run the app through visual studio go terminal will not work because it uses your global python settings not the local packages needed to flask app so you need to run it through terminal.


## TODO LIST.
1. Still need a page that directly links to spotify authentication on our website.
2. Still need to redirect artist page but bigger problem is to redirect from our base dataset to one that is customized for the user.
3. Also need to figure out how to run the website through vcm if that is what we eventually want to do.





