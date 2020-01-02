from datetime import datetime

import pytz
from flask_wtf import Form
from wtforms import (BooleanField, DateTimeField, SelectField, SelectMultipleField, StringField)
from wtforms.validators import URL, AnyOf, DataRequired, Regexp
# can be used to create form from sqlalchemy model directly
from wtforms.ext.sqlalchemy.orm import model_form

from fyyur.models import Artist, Venue

STATES = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]
GENRES = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]
US_TZS = [tz for tz in pytz.all_timezones if tz.startswith("US")]


class ShowForm(Form):
    # make sure artist id exists in DB
    artist_id = StringField('Artist ID', validators=[DataRequired(),
                                                     AnyOf([x.id for x in Artist.query.all()])])
    # make sure venue id exists in DB
    venue_id = StringField('Venue ID', validators=[DataRequired(),
                                                   AnyOf([x.id for x in Venue.query.all()])])
    start_time = DateTimeField('Start Time', validators=[DataRequired()], default=datetime.today())
    time_zone = SelectField(
        'Time Zone',
        validators=[DataRequired()],
        # sequence of (value, label) pairs - value and label the same
        choices=list(zip(*[US_TZS, US_TZS])))


class VenueForm(Form):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=STATES)
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Phone',
                        validators=[
                            Regexp(r'\d{10}',
                                   message='Phone number must be in format 1234567890')
                        ])
    genres = SelectMultipleField(
        'Genres',
        validators=[DataRequired()],
        choices=GENRES)
    website = StringField('Website', validators=[URL(message='Website link is not a valid URL')])
    image_link = StringField('Image Link',
                             validators=[URL(message='Image link is not a valid URL')])
    facebook_link = StringField('Facebook Link',
                                validators=[URL(message='Facebook link is not a valid URL')])
    seeking_talent = BooleanField('Seeking Talent')
    seeking_description = StringField('Seeking Talent Description')


class ArtistForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', validators=[DataRequired()], choices=STATES)
    phone = StringField(
        # TODO implement validation logic for state
        'Phone')
    genres = SelectMultipleField(
        'Genres',
        validators=[DataRequired()],
        choices=GENRES)
    website = StringField('Website', validators=[URL(message='Website link is not a valid URL')])
    image_link = StringField('Image Link',
                             validators=[URL(message='Image link is not a valid URL')])
    facebook_link = StringField('Facebook Link',
                                validators=[URL(message='Facebook link is not a valid URL')])
    seeking_venue = BooleanField('Seeking Venue')
    seeking_description = StringField('Seeking Venue Description')
