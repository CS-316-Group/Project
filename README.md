

# HOW TO LOG IN TO THE DATABASE.

Run the following commands in the terminal: 
1. `ssh vcm@vcm-13360.vm.duke.edu`
2. 	enter database password
3. `cd /srv/ProjectDatabase`
4. `docker-compose down`
5. `docker-compose up -d`

Database name: production
Database username: `dbuser`

# RUNNING DYNAMIC SQL QUERIES
`psql -h vcm-13360.vm.duke.edu -p 5432 -U dbuser -W -d production -af test-sample.sql > test-sample.out`


# CREATING THE TABLES AND LOADING THEM  

## From Python

To create the tables: from the src folder, run the command `python -m d03_database_interaction.db_setup` 
This script calls a function from create_sql_tables.py (also in d03_database_interaction/), while by default, 
drops all the existing tables and recreates them. 

To load the tables with data, we need users to visit the login page for new users in the Flask app, 
and enter their desired username. After that, users will be redirected to the Spotify login page, 
where they will be prompted to give our app permission to access their Spotify data. After receiving
authorization, we pull raw data from the Spotify API endpoint, pass it through the data cleaning 
functions found in `d01_data_processing`, and insert the data to the database through functions found 
in `d04_app`. 

## Directly on the VM using the PSQL command line tool
To create the tables: put the create SQL statements and any trigger statements into a file called create.sql. 
Run the command `\i /home/vcm/create.sql`,

To load data into the tables: Create a load.sql, and run the command `\i /home/vcm/load.sql`.



# SETTING UP SERVERS AND DEPLOYING APP.

We chose to deploy our app nginx using as the server and uWSGI as the protocol server. To configure uWSGI, we created app.ini in d04_app folder. In the `app.ini` file, we specified how many processes and threads to use for the website. We also specificed the socket to for uwsgi. Next we cloned our project into our database stored in the group virtual machine. Next, we created a virtual environment and installed the necessary files needed for the project to work. Next  adjusted the firewall for our vm to allow for traffic from all HTTP ports. Next, we used nano to create a .service unit filled called ap. In that file, we created a unit and service blocker that communicates with nginx about where our app is stored and to use uwsgi to handle protocol. Next we configured Nginx by creating a new server block in the new file called app. In the server block, we definded listen as 80 to allow for http trafic. Next we set the server_name to our appi address and changed the localation to pass through uwsgi. We then restared the nginx to get our app running.




# WHERE TO STORE CREDENTIALS IN THE PROJECT FOLDER STRUCTURE
To gain access to the Spotify API, you need to place the "credentials.yml" file into the following location: `conf/local/credentials.yml`. This file is git-ignored so that it will not be pushed to GitHub. 

The correct folder structure looks like: 
```
├── conf    
|   ├── base
|   └── local 
|       └── credentials.yml
├── data_examples                    
├── notebooks                     
├── src                    
├── .gitignore                    
├── __init__.py
└── README.md 

```
Within the "credentials.yml", you should have the Spotify developer account credentials and the database
username and password. The contents of the file should look like the following: 

```
spotify_dev_creds:
  spotify_client_id: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  spotify_client_secret: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

postgres:
    user: "your_username"
    passphrase: "your_passphrase"
```


# RUNNING THE APP THROUGH LOCAL HOST.
1. First step. Create a virtual environment through anaconda.
`conda create -n flask_app python=3.7.3`


2. Install all the dependencies in your application
`pip3 install -r requirements.txt`
(when available)
Dependencies are all the libraries needed to run the app, eg. flask, sqlalchemy. 
2a. To generate the requirements.text run `pip freeze >> requirements.txt`
Run this anytime you use new libraries in the project. 

3. Navigate to the src folder and run `python -m d04_app.app`

<!-- 3. Export the Flask app as follows: 


3a. `export FLASK_APP=app.py `
3b.  `export FLASK_ENV=development`
3c. `flask run` 
 -->
<!-- ** You might need to modify commands a little bit if computer is not a MAC** -->


