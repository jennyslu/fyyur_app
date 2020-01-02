"""
This is where you define the models of your application.
This may be split into several modules in the same way as views.py.
----------------------------------------------------------------------------#
 Models.
----------------------------------------------------------------------------#
"""
from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql

from fyyur import db


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    # limit phone to 10 digits
    phone = db.Column(db.String(10))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    # tell the DB to calculate the value itself
    # use server_default instead of default - should end up in CREATE TABLE
    time_created = db.Column(postgresql.TIMESTAMP(timezone=True), server_default=func.now())
    # server_onupdate doesn't do anything serverside
    time_updated = db.Column(postgresql.TIMESTAMP(timezone=True), onupdate=func.now())
    venue_shows = db.relationship('Show', backref='venue_shows', lazy=True)


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    # limit phone to 10 digits
    phone = db.Column(db.String(10))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    # tell the DB to calculate the value itself
    # use server_default instead of default - should end up in CREATE TABLE
    time_created = db.Column(postgresql.TIMESTAMP(timezone=True), server_default=func.now())
    # server_onupdate doesn't do anything serverside
    time_updated = db.Column(postgresql.TIMESTAMP(timezone=True), onupdate=func.now())
    artist_shows = db.relationship('Show', backref='artist_shows', lazy=True)


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.TIMESTAMP(timezone=True))
    venue = db.relationship('Venue', backref='show_venue')
    artist = db.relationship('Artist', backref='show_artist')
