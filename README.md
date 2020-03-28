# HOW TO CREATE AND LOAD DATABASE.
1. `ssh vcm@vcm-13360.vm.duke.edu`
2. password:merdr7vuEr
3. `cd /srv/ProjectDatabase`
4. `docker-compose down`
5. `docker-compose up -d`
Separate window:
6. Might have to run this code to install psql: `sudo apt-get install postgresql-client`
7. `psql -h vcm-13360.vm.duke.edu -p 5432 -U dbuser -W -d production`
8. password is `example`

File creating all the tables and their references is create.sql in tge srv/ProjectDatabase folder.
Loading data = load.sql

9. Create tables: Run the command `\i /home/vcm/create.sql`
10. Load data: Run the command `\i /home/vcm/load.sql`


Running dynamic sql queries.
`psql production  -af test-sample.sql > test-sample.out`

# HOW TO SET UP CREDS FILE 

To gain access to the Spotify API, you need to place the "credentials.yml" file into the following location: `conf/local/credentials.yml`. The correct folder structure looks like: 
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
