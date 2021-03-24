from app import app, db, Venue, Artist, Show
from enums import Genre, State

# with app.app_context():
db.drop_all()
db.create_all()

genres = list(dict(Genre.choices()).keys())

#---------------------------------#
# Add Venues 
#---------------------------------#
v1 = Venue(**{
    "name": "The Musical Hop",
    "genres": [genres[i] for i in [10, 15, 2, 5]],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
})

v2 = Venue(**{
    "name": "The Dueling Pianos Bar",
    "genres": [genres[i] for i in [2, 14, 7]],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
})

v3 = Venue(**{
    "name": "Park Square Live Music & Coffee",
    "genres": [genres[i] for i in [14, 1, 9, 8]],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
})

v4 = Venue(**{
    "name": "The Rockery",
    "genres": [genres[i] for i in [0,2,4,6,8,10,15]],
    "address": "128 Robinsons Road",
    "city": "Singapore",
    "state": "SG",
    "phone": "+65-9999-9999",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": True,
    "seeking_description": "Some text here",
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
})

db.session.add(v1)
db.session.add(v2)
db.session.add(v3)
db.session.add(v4)
db.session.commit()

#---------------------------------#
# Add Artists 
#---------------------------------#
a1 = Artist(**{
    "name": "Guns N Petals",
    "genres": [genres[16]],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
})

a2 = Artist(**{
    "name": "Matt Quevedo",
    "genres": [genres[10]],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",

})

a3 = Artist(**{
    "name": "The Wild Sax Band",
    "genres": [genres[10], genres[2]],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
})

a4 = Artist(**{
    "name": "Sonic the Hedgehog",
    "city": "Mobius",
    "genres": [],
    "state": "$$",
    "seeking_venue": True,
    "image_link": "https://decider.com/wp-content/uploads/2020/03/sonic-the-hedgehog.jpg",
    "seeking_description": "The cutest and fastest hedgehog in the universe!"
})

db.session.add(a1)
db.session.add(a2)
db.session.add(a3)
db.session.add(a4)
db.session.commit()

#---------------------------------#
# Add Shows 
#---------------------------------#
from datetime import datetime

show1 = Show(start_time=datetime(2020,5,21,21,30,0))
show1.artist = a3
show1.venue = v1

show2 = Show(start_time=datetime(2022, 6, 15, 23))
show2.artist = a3
show2.venue = v1

show3 = Show(start_time=datetime(2019, 5, 1, 21, 30))
show3.artist = a1
show3.venue = v2

show4 = Show(start_time=datetime(2021, 10, 1, 21, 30))
show4.artist = a2
show4.venue = v1

show5 = Show(start_time=datetime(2019, 12, 31, 21, 30))
show5.artist = a2
show5.venue = v3

show6 = Show(start_time=datetime(2021, 6, 11, 21))
show6.artist = a4
show6.venue = v1

db.session.add_all([
    show1, show2, show3, show4, show5, show6
])
db.session.commit()

