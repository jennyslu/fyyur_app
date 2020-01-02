from datetime import datetime

import babel
import dateutil.parser
import pandas as pd
import pytz
from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.sql import func

from fyyur import app, db
from fyyur.forms import ArtistForm, ShowForm, VenueForm
from fyyur.models import Artist, Show, Venue

# ----------------------------------------------------------------------------#
#  Jinja Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
#  Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # substitute NULLs in state and city with N/A - this will be a group
    city_venues = db.session.query(func.coalesce(Venue.city, 'N/A'),
                                   func.coalesce(Venue.state, 'N/A'), func.array_agg(Venue.id),
                                   func.array_agg(Venue.name)).group_by(Venue.city,
                                                                        Venue.state).all()
    data = []
    for venue_data_tuple in city_venues:
        city_venue_dict = {}
        city_venue_dict["city"] = venue_data_tuple[0]
        city_venue_dict["state"] = venue_data_tuple[1]
        city_venue_dict["venues"] = []
        for i in range(len(venue_data_tuple[2])):
            venue_dict = {}
            venue_dict["id"] = venue_data_tuple[2][i]
            venue_dict["name"] = venue_data_tuple[3][i]
            # count the number of shows linked to Venue that have start_time after now
            venue_dict["num_upcoming_shows"] = sum([
                x.start_time > datetime.now(pytz.utc)
                for x in Venue.query.get(venue_data_tuple[2][i]).venue_shows
            ])
            city_venue_dict["venues"].append(venue_dict)
        data.append(city_venue_dict)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue_data = Venue.query.get(venue_id)
    data = venue_data.__dict__
    data["past_shows"] = []
    data["upcoming_shows"] = []
    for show in venue_data.venue_shows:
        # show is in the past
        if show.start_time < datetime.now(pytz.utc):
            data["past_shows"].append({
                "artist_id": show.artist.id, "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%dT%X")
            })
        else:
            data["upcoming_shows"].append({
                "artist_id": show.artist.id, "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%dT%X")
            })
    data["past_shows_count"] = len(data["past_shows"])
    data["upcoming_shows_count"] = len(data["upcoming_shows"])
    return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    # lower to ensure case insensitive
    venues = Venue.query.filter(func.lower(Venue.name).like("%{}%".format(
        search_term.lower()))).all()
    data = []
    for venue in venues:
        data.append({
            "id": venue.id, "name": venue.name, "num_upcoming_shows": sum(
                [x.start_time > datetime.now(pytz.utc) for x in venue.venue_shows])
        })
    response = {"count": len(venues), "data": data}
    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        new_venue_data = request.form.to_dict()
        # get list of genres
        new_venue_data["genres"] = request.form.getlist('genres')
        # convert to boolean -- if not checked key won't exist
        new_venue_data["seeking_talent"] = new_venue_data.get("seeking_talent") == "y"
        # remove empty string values
        new_venue_data = {k: v for k, v in new_venue_data.items() if v != ''}
        # make sure to avoid PK error with data that may already be inserted
        new_venue_data["id"] = db.session.query(func.max(Venue.id)).first()[0] + 1
        new_venue = Venue(**new_venue_data)
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('{} was successfully listed with ID {}!'.format(new_venue.name, new_venue.id))
        return redirect(url_for('show_venue', venue_id=new_venue.id))
    # rollback if fail to avoid potential implicit commits
    except Exception as e:
        db.session.rollback()
        # on unsuccessful db insert, flash an error instead.
        flash("An error occurred while trying to add new venue: {}".format(e), "error")
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        deleted_venue_name = venue.name
        db.session.delete(venue)
        db.session.commit()
        flash('{} was successfully deleted'.format(deleted_venue_name))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while trying to delete {}: {}".format(venue_id, e), "error")
    finally:
        db.session.close()


@app.route('/venues/<int:venue_id>/edit', methods=['GET', 'POST'])
def edit_venue(venue_id):
    venue_to_edit = Venue.query.get(venue_id)
    # pre-populate the form with already existing venue data
    if request.method == "GET":
        # populate form with values from venue with ID <venue_id>
        form = VenueForm(obj=venue_to_edit)
        return render_template('forms/edit_venue.html', form=form, venue=venue_to_edit)
    # submission was made to edit venue
    elif request.method == "POST":
        try:
            updated_venue_dict = request.form.to_dict()
            # get list of genres
            updated_venue_dict["genres"] = request.form.getlist('genres')
            # convert to boolean -- if not checked key won't exist
            updated_venue_dict["seeking_talent"] = updated_venue_dict.get("seeking_talent") == "y"
            # remove empty string values
            updated_venue_dict = {k: v for k, v in updated_venue_dict.items() if v != ''}
            # update attributes of the venue object
            for key, value in updated_venue_dict.items():
                setattr(venue_to_edit, key, value)
            # commit the updates
            db.session.commit()
            # on successful db insert, flash success
            flash('{} was successfully updated!'.format(venue_id))
            return redirect(url_for('show_venue', venue_id=venue_id))
        except Exception as e:
            db.session.rollback()
            # on unsuccessful db insert, flash an error instead.
            flash("An error occurred while trying to update venue: {}".format(e), "error")
        finally:
            db.session.close()
        return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    # lower to ensure case insensitive
    artists = Artist.query.filter(func.lower(Artist.name).like("%{}%".format(
        search_term.lower()))).all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id, "name": artist.name, "num_upcoming_shows": sum(
                [x.start_time > datetime.now(pytz.utc) for x in artist.artist_shows])
        })
    response = {"count": len(artists), "data": data}
    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_data = Artist.query.get(artist_id)
    data = artist_data.__dict__
    data["past_shows"] = []
    data["upcoming_shows"] = []
    for show in artist_data.artist_shows:
        # show is in the past
        if show.start_time < datetime.now(pytz.utc):
            data["past_shows"].append({
                "venue_id": show.venue.id, "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%dT%X")
            })
        else:
            data["upcoming_shows"].append({
                "venue_id": show.venue.id, "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%dT%X")
            })
    data["past_shows_count"] = len(data["past_shows"])
    data["upcoming_shows_count"] = len(data["upcoming_shows"])
    return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        new_artist_data = request.form.to_dict()
        # get list of genres
        new_artist_data["genres"] = request.form.getlist('genres')
        # convert to boolean -- if not checked key won't exist
        new_artist_data["seeking_venue"] = new_artist_data.get("seeking_venue") == "y"
        # remove empty string values
        new_artist_data = {k: v for k, v in new_artist_data.items() if v != ''}
        # make sure to avoid PK error with data that may already be inserted
        new_artist_data["id"] = db.session.query(func.max(Artist.id)).first()[0] + 1
        new_artist = Artist(**new_artist_data)
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('{} was successfully listed with ID {}!'.format(new_artist.name, new_artist.id))
        return redirect(url_for('show_artist', artist_id=new_artist.id))
    # rollback if fail to avoid potential implicit commits
    except Exception as e:
        db.session.rollback()
        # on unsuccessful db insert, flash an error instead.
        flash("An error occurred while trying to add new artist: {}".format(e), "error")
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/artists/<int:artist_id>/edit', methods=['GET', 'POST'])
def edit_artist(artist_id):
    artist_to_edit = Artist.query.get(artist_id)
    # pre-populate the form with already existing venue data
    if request.method == "GET":
        # populate form with values from venue with ID <venue_id>
        form = ArtistForm(obj=artist_to_edit)
        return render_template('forms/edit_artist.html', form=form, artist=artist_to_edit)
    # submission was made to edit venue
    elif request.method == "POST":
        try:
            updated_venue_dict = request.form.to_dict()
            # get list of genres
            updated_venue_dict["genres"] = request.form.getlist('genres')
            # convert to boolean -- if not checked key won't exist
            updated_venue_dict["seeking_venue"] = updated_venue_dict.get("seeking_venue") == "y"
            # remove empty string values
            updated_venue_dict = {k: v for k, v in updated_venue_dict.items() if v != ''}
            # update attributes of the venue object
            for key, value in updated_venue_dict.items():
                setattr(artist_to_edit, key, value)
            # commit the updates
            db.session.commit()
            # on successful db insert, flash success
            flash('{} was successfully updated!'.format(artist_id))
            return redirect(url_for('show_artist', artist_id=artist_id))
        except Exception as e:
            db.session.rollback()
            # on unsuccessful db insert, flash an error instead.
            flash("An error occurred while trying to update venue: {}".format(e), "error")
        finally:
            db.session.close()
        return render_template('pages/home.html')


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        deleted_artist_name = artist.name
        db.session.delete(artist)
        db.session.commit()
        flash('{} was successfully deleted'.format(deleted_artist_name))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while trying to delete {}: {}".format(artist_id, e), "error")
    finally:
        db.session.close()


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id, "venue_name": show.venue.name, "artist_id": show.artist_id,
            "artist_name": show.artist.name, "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%X")
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    import pdb
    pdb.set_trace()
    try:
        new_show_data = request.form.to_dict()
        new_show_data["artist_id"] = int(new_show_data["artist_id"])
        new_show_data["venue_id"] = int(new_show_data["venue_id"])
        new_show_data["start_time"] = pd.Timestamp(
            new_show_data["start_time"], tz=new_show_data.pop("time_zone")).strftime("%Y-%m-%d %X %z")
        # make sure to avoid PK error with data that may already be inserted
        new_show_data["id"] = db.session.query(func.max(Show.id)).first()[0] + 1
        new_show = Show(**new_show_data)
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('New show was successfully listed with ID {}!'.format(new_show.id))
        return redirect(url_for('shows'))
    # rollback if fail to avoid potential implicit commits
    except Exception as e:
        db.session.rollback()
        # on unsuccessful db insert, flash an error instead.
        flash("An error occurred while trying to add new show: {}".format(e), "error")
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
