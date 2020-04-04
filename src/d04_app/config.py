from d00_utils.load_confs import load_credentials, load_paths, load_parameters

db_paths = load_paths()['db_paths']
db_creds = load_credentials()['postgres']
params = load_parameters()

username, passphrase = db_creds['user'], db_creds['passphrase']
host, name = db_paths['db_host'], db_paths['db_name']

SQLALCHEMY_DATABASE_URI = f'postgres://{username}:{passphrase}@{host}/{name}'

SQLALCHEMY_ECHO = True
DEBUG = params['debug_mode_on']