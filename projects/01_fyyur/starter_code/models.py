from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy() 

# Removed. Refer genres from enums.
# artist_genres = db.Table('artist_genres', 
#   db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
#   db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
# )

# venue_genres = db.Table('venue_genres', 
#   db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
#   db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
# )

# class Genre(db.Model):
#   __tablename__ = 'genre'
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String(120), nullable=True)

class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean)
  seeking_description = db.Column(db.String())
  genres = db.Column(db.ARRAY(db.String(30)))
#   genres = db.relationship('Genre', 
#       secondary=venue_genres, 
#       backref=db.backref('venue', lazy=True),
#   ) 
  #set lazy to "joined" to get all the info from Show in a single SQL statement when querying venue
  shows = db.relationship('Show', lazy="joined", cascade="save-update, delete", backref='venue')

class Artist(db.Model):
  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean)
  seeking_description = db.Column(db.String())
  genres = db.Column(db.ARRAY(db.String(30)))
#   genres = db.relationship('Genre', 
#       secondary=artist_genres, 
#       backref=db.backref('artist', lazy=True)
# ) 
  #set lazy to "joined" to get all the info from Show in a single SQL statement when querying artist
  shows = db.relationship('Show', lazy="joined", cascade="save-update, delete", backref='artist')


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete="CASCADE"))
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete="CASCADE"))
  start_time = db.Column(db.DateTime)


