#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import re
from datetime import datetime

from flask_wtf import FlaskForm as Form
from wtforms import (
    StringField, 
    SelectField, 
    SelectMultipleField, 
    DateTimeField, 
    BooleanField
)
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Optional

from enums import Genre, State

#----------------------------------------------------------------------------#
# Custom Validators
#----------------------------------------------------------------------------#

def is_valid_phone(form, field):
    """ Validate phone numbers like:
    1234567890 - no space
    123.456.7890 - dot separator
    123-456-7890 - dash separator
    123 456 7890 - space separator

    Patterns:
    000 = [0-9]{3}
    0000 = [0-9]{4}
    -.  = ?[-. ]

    Note: (? = optional) 
    """
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    number = field.data
    if not regex.match(number):
        raise ValidationError('Invalid phone.')

def is_valid_genre(form, field):
    if not set(field.data).issubset(dict(Genre.choices()).keys()):
        raise ValidationError('Invalid genre.')

def is_valid_state(form, field):
    if field.data not in dict(State.choices()).keys():
        raise ValidationError('Invalid state.')

#----------------------------------------------------------------------------#
# Forms
#----------------------------------------------------------------------------#

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), is_valid_state],
        choices = State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[is_valid_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), is_valid_genre],
        choices = Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
    )
    website = StringField(
        'website'
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), is_valid_state],
        choices = State.choices()
    )
    phone = StringField(
        'phone', validators=[is_valid_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), is_valid_genre],
        choices= Genre.choices()
     )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
     )
    website = StringField(
        'website'
     )
    seeking_venue = BooleanField( 
        'seeking_venue'
    )
    seeking_description = StringField(
            'seeking_description'
     )

