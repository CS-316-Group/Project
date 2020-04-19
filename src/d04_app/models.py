from sqlalchemy import sql, orm
from d04_app.app import db

#to do-check the uniqueness of each attribute.
#albums = orm.relationshio('Albums')-it is unclear whether 
#this is needed because as defined on the 
#er diagram, there is no artist associated with 
#album. i think each one to many relationship might need a foreign key id. 
#double check that they do.

class Artists(db.Model):
    __tablename__ = 'artists'
    id = db.Column('id', db.String(200), primary_key=True)
    artist_name = db.Column('artist_name',db.String(200), unique=True)
    pop = db.Column('pop',db.Integer(), unique=False)
    followers = db.Column('followers',db.Integer(), unique=False)
    image_url = db.Column('image_url', db.String(400), unique= False)
    #not sure about this to specify one to many relationship between classes.
    topartists = orm.relationship('Topartists')
    created = orm.relationship('Createdby')
    def __repr__(self):
       return '<Artist: {}>'.format(self.artist_name) 

class Listeners(db.Model):
    __tablename__ = 'listeners'
    listener_id = db.Column('listener_id', db.String(200), primary_key=True)
    display_name = db.Column('display_name', db.String(200), nullable= False)
    username = db.Column('username', db.String(200), nullable = False)
    password = db.Column('password', db.String(200), nullable = False)
    followers = db.Column('followers',db.Integer(), nullable = False)
    image_url = db.Column('image_url',db.String(400), unique= False, nullable = False)

    #not sure about this to specify one to many relationship between classes.
    topartists = orm.relationship('Topartists') #from blog miguelgrinberg
    toptracks = orm.relationship('Toptracks')


class Tracks(db.Model):
    __tablename__ = 'tracks'
    id = db.Column('id', db.String(200), primary_key=True)
    track_name = db.Column('track_name', db.String(200), nullable= False)
    pop = db.Column('pop',db.Integer(), nullable = False)
    review_url = db.Column('review_url',db.String(400), unique= False, nullable = False)
    acoustic = db.Column('acousticness',db.Numeric() , nullable = False)
    danceability = db.Column('danceability',db.Numeric(), nullable = False)
    energy = db.Column('energy',db.Numeric() , nullable = False)
    instrumalness = db.Column('instrumentalness',db.Numeric() , nullable = False)
    liveness = db.Column('liveness',db.Numeric() , nullable = False)
    loudness = db.Column('loudness',db.Numeric() , nullable = False)
    mode = db.Column('mode',db.Integer(), nullable = False)
    speechiness = db.Column('speechiness',db.Numeric(), nullable = False)
    tempo = db.Column('tempo',db.Numeric(), nullable = False)
    time_signature = db.Column('time_signature',db.Integer() , nullable = False)
    valence = db.Column('valence',db.Numeric(), nullable = False)
    tracksonalbum=orm.relationship('Albumcontainstrack')


class Albums(db.Model):
    __tablename__ = 'albums'
    id = db.Column('id', db.String(200), primary_key=True)
    name = db.Column('name', db.String(200), nullable= False)
    album_type = db.Column('album_type', db.String(200), nullable = False)
    image_url = db.Column('image_url',db.String(400), unique= False, nullable = False)
    date= db.Column('date', db.String(200), unique = False)
    #not sure about this to specify one to many relationship between classes.
    tracksonalbum=orm.relationship('Albumcontainstrack')


class Topartists(db.Model):
    __tablename__ = 'topartists'
    listener_id = db.Column('listener_id', db.String(200), db.ForeignKey('listeners.id'), primary_key = True)
    artist_id = db.Column('artist_id', db.String(200), db.ForeignKey('artists.id'), primary_key = True)
    time_span = db.Column('time_span', db.String(200), primary_key=True)

   
class Toptracks(db.Model):
    __tablename__ = 'toptracks'
    listener_id = db.Column('listener_id', db.String(200), db.ForeignKey('listeners.id'), primary_key = True)
    track_id = db.Column('track_id', db.String(200), db.ForeignKey('tracks.id'), primary_key = True)
    time_span = db.Column('time_span', db.String(200), primary_key=True)

#to-do this table seems redundant.
class Createdby(db.Model):
    __tablename__ = 'createdby'
    artist_id = db.Column('artist_id', db.String(200), db.ForeignKey('artists.id'), primary_key = True)
    track_id = db.Column('track_id', db.String(200), db.ForeignKey('tracks.id'), primary_key = True)

class Albumcontainstrack(db.Model):
    __tablename__ = 'albumcontainstrack'
    track_id = db.Column('track_id', db.String(200), db.ForeignKey('tracks.id'), primary_key = True)
    album_id = db.Column('album_id', db.String(200), db.ForeignKey('albums.id'), primary_key = True)

class Genre(db.Model):
     __tablename__ = 'genre'
     genre_name = db.Column('genre_name', db.String(200), primary_key= True)

class Artisthasgenre(db.Model):
    __tablename__ = 'artisthasgenre'
    genre_name = db.Column('genre_name', db.String(200), db.ForeignKey('genre.genre_name'), primary_key = True)
    artist_id = db.Column('artist_id', db.String(200), db.ForeignKey('artists.id'), primary_key = True)

class Albumhasgenre(db.Model):
    __tablename__ = 'albumhasgenre'
    genre_name = db.Column('genre_name', db.String(200), db.ForeignKey('genre.genre_name'), primary_key = True)
    album_id = db.Column('album_id', db.String(200), db.ForeignKey('albums.id'), primary_key = True)


#can also define 
#def __repr__(self):
#       return '<User {}>'.format(self.username)  
#which tells python how to print objects of this class.
