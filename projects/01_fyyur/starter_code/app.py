#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import logging
from logging import Formatter, FileHandler
from collections import defaultdict
from datetime import datetime

import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for, 
    jsonify, 
    abort 
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import Form

from forms import ShowForm, VenueForm , ArtistForm
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)

db.init_app(app)

app.app_context().push()

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  # TODO: replace with real venues data.
  
  # old implementation (keeping for future review)
  # temp = defaultdict(list)
  # for v in db.session.query(Venue.id, Venue.name, Venue.city, Venue.state).all():
  #   temp[(v.city, v.state)].append({
  #     "id": v.id,
  #     "name": v.name, 
  #   })
  # areas = [
  #   {"city": city, "state": state, "venues": venues}
  #   for (city, state), venues in temp.items()
  # ]

  # alternative implementation 
  areas = []
  venues = Venue.query.all()

  places = Venue.query.distinct(Venue.city, Venue.state).all()

  for place in places:
      areas.append({
          'city': place.city,
          'state': place.state,
          'venues': [{
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': len([s for s in venue.shows if s.start_time > datetime.now()])
          } for venue in venues if
              venue.city == place.city and venue.state == place.state]
      })
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venue with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get("search_term", "")
  venues = db.session.query(Venue).filter(Venue.name.ilike(f"%{search_term}%")).all()

  response={
    "count": len(venues),
    "data": [
      { "id": v.id, 
        "name": v.name, 
        "num_upcoming_shows": len([s for s in v.shows if s.start_time > datetime.now()])
      } for v in venues]
  }
  return render_template('pages/search_venues.html', 
                          results=response, 
                          search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


  # v = db.session.query(Venue).get(venue_id)  
  # shows = db.session.query(Show.start_time, Artist.id, Artist.name, Artist.image_link).\
  #               join(Artist).\
  #               filter(Show.venue_id == venue_id).\
  #               order_by(Show.start_time).\
  #               all()
  # def parse_shows(start_time, artist_id, artist_name, artist_image_link):
  #   return {
  #     "artist_id": artist_id, 
  #     "artist_name": artist_name,
  #     "artist_image_link": artist_image_link,
  #     "start_time": str(start_time)
  #   }
  # upcoming_shows = [parse_shows(*s) for s in shows if s[0] > datetime.now()]
  # past_shows = [parse_shows(*s) for s in shows if s[0] <= datetime.now()]

  v = Venue.query.get_or_404(venue_id)
  past_shows = []
  upcoming_shows = []
  for show in v.shows:
    info = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
      past_shows.append(info)
    else:
      upcoming_shows.append(info)

  data = {
    "id": v.id,
    "name": v.name,
    "genres": v.genres, 
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  #   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  form = VenueForm(request.form, meta = {'csrf': False})
  if form.validate():
    try:
      venue = Venue()
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
      print(e)
      flash('Error in listing venue. Please try again.')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    err_msg = []
    for field, err in form.errors.items():
      err_msg.append(field + '-' + '|'.join(err))
    flash('Errors: ' + str(err_msg))

  return render_template('pages/home.html')
 
  # error = False
  # try:  
  #   formdata = {k: v for k,v in request.form.items() if k != 'genres'}
  #   seeking_talent = request.form.get('seeking_talent') 
  #   if seeking_talent:
  #     formdata['seeking_talent'] = True
  #   venue = Venue(**formdata)

  #   genres = db.session.query(Genre).filter(Genre.name.in_(request.form.getlist('genres'))).all()
  #   for g in genres:
  #     g.venue.append(venue)
  #   db.session.add(venue)
  #   db.session.commit()
  # except: 
  #   error = True
  #   db.session.rollback()
  #   print(sys.exc_info())
  # finally:
  #   db.session.close()
  # if error:
  #   abort(400)
  # else:
  #   flash('Venue ' + request.form['name'] + ' was successfully listed!')  #   
  #   return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return ('', 200)


#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form, meta = {'csrf': False})
  if form.validate():
    try:
      venue = Venue.query.get_or_404(venue_id)
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      flash('Venue update success!')
    except ValueError as e:
      print(e)
      flash('Error in updating venue. Please try again.')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    err_msg = []
    for field, err in form.errors.items():
      err_msg.append(field + '-' + '|'.join(err))
    flash('Errors: ' + str(err_msg))

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term", "")
  data = db.session.query(Artist).filter(Artist.name.ilike(f"%{search_term}%")).all()

  response={
    "count": len(data),
    "data": [{
      "id": d.id,
      "name": d.name,
      "num_upcoming_shows": len([s for s in d.shows if s.start_time > datetime.now()]),
    } for d in data]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # artist = db.session.query(Artist).get(artist_id)
  # shows = db.session.query(Show.start_time, Venue.id, Venue.name, Venue.image_link).\
  #               join(Venue).\
  #               filter(Show.artist_id == artist_id).\
  #               order_by(Show.start_time).\
  #               all()
  # def parse_shows(start_time, venue_id, venue_name, venue_image_link):
  #   return {
  #     "venue_id": venue_id, 
  #     "venue_name": venue_name,
  #     "venue_image_link": venue_image_link,
  #     "start_time": str(start_time)
  #   }
  # upcoming_shows = [parse_shows(*s) for s in shows if s[0] > datetime.now()]
  # past_shows = [parse_shows(*s) for s in shows if s[0] <= datetime.now()]

  artist = Artist.query.get_or_404(artist_id)
  past_shows = []
  upcoming_shows = []
  for show in artist.shows:
    info = {
      "venue_id": show.venue_id, 
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link, 
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
      past_shows.append(info)
    else:
      upcoming_shows.append(info)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  form = ArtistForm(request.form, meta = {'csrf': False})
  if form.validate():
    try:
      artist = Artist()
      form.populate_obj(artist)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
      print(e)
      flash('Error in listing artist. Please try again.')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    err_msg = []
    for field, err in form.errors.items():
      err_msg.append(field + '-' + '|'.join(err))
    flash('Errors: ' + str(err_msg))

  return render_template('pages/home.html')

#  Update Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form, meta = {'csrf': False})
  if form.validate():
    try:
      artist = Artist.query.get_or_404(artist_id)
      form.populate_obj(artist)
      db.session.add(artist)
      db.session.commit()
      flash('Update success!')
    except ValueError as e:
      print(e)
      flash('Error updating artist. Please try again.')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    err_msg = []
    for field, err in form.errors.items():
      err_msg.append(field + '-' + '|'.join(err))
    flash('Field error: ' + str(err_msg))

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  shows = Show.query.order_by('start_time').all()
  data = [{
    "venue_id": s.venue.id,
    "venue_name": s.venue.name,
    "artist_id": s.artist.id,
    "artist_name": s.artist.name,
    "artist_image_link": s.artist.image_link,
    "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M")
  } for s in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  form = ShowForm(request.form, meta = {'csrf': False})

  if form.validate():
    try:
      show = Show()
      form.populate_obj(show)
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
    except ValueError as e:
      print(e)
      flash('Error in listing show. Please try again.')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    err_msg = []
    for field, err in form.errors.items():
      err_msg.append(field + '-' + '|'.join(err))
    flash('Errors: ' + str(err_msg))

  return render_template('pages/home.html')


#  Error Routes
#  ----------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
