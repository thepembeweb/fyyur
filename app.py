# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys
from sqlalchemy import func
from flask import render_template, request, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from forms import *
from config import app
from models import Venue, Artist, Show, db
from utils import format_datetime


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    """ Render the home page """

    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    """ Display venues """

    data = []
    venue_places = db.session.query(Venue.city, Venue.state).distinct()

    for venue_place in venue_places:
        venues_data = []
        for venue in Venue.query.filter_by(
                city=venue_place.city).filter_by(
                state=venue_place.state).all():
            venues_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': 0
            })
            data.append({
                'city': venue_place.city,
                'state': venue_place.state,
                'venues': venues_data
            })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    """ Search venues """

    data = []
    search_term = request.form.get('search_term', '')

    venues = Venue.query.filter(
        Venue.name.ilike(
            "%{}%".format(search_term))).all()

    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_shows": 0
        })
    response = {
        "count": len(venues),
        "data": data
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    """ Display venue by Id """

    venue = Venue.query.get(venue_id)

    past_shows_result = Show.query.filter(
        Show.venue_id == venue_id,
        Show.start_time < datetime.now()).all()
    upcoming_shows_result = Show.query.filter(
        Show.venue_id == venue_id,
        Show.start_time > datetime.now()).all()

    past_shows = []
    upcoming_shows = []

    for past_show in past_shows_result:
        past_shows.append({
            "artist_id": past_show.artist.id,
            "artist_name": past_show.artist.name,
            "artist_image_link": past_show.artist.image_link,
            "start_time": past_show.start_time.strftime("%m/%d/%Y, %H:%M"),
        })

    for upcoming_show in upcoming_shows_result:
        upcoming_shows.append({
            "artist_id": upcoming_show.artist.id,
            "artist_name": upcoming_show.artist.name,
            "artist_image_link": upcoming_show.artist.image_link,
            "start_time": upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M"),
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "genres": [venue.genres],
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
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
    """ Create a venues """

    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form, meta={'csrf': False})

    if form.validate():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                address=form.address.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                seeking_talent=form.seeking_talent.data,
                website_link=form.website_link.data,
                seeking_description=form.seeking_description.data)
            db.session.add(venue)
            db.session.commit()
            flash(f'Venue {request.form["name"]} was successfully listed!')
            return render_template('pages/venues.html')
        except BaseException:
            db.session.rollback()
            flash(f'Venue {request.form["name"]} could not be listed.')
        finally:
            db.session.close()
    else:
        flash(f'Error occured while trying to create Venue: {form.name.data}.')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    """ Delete a venue by Id """

    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(f'An error occurred. Venue {venue_id} could not be deleted.')
    if not error:
        flash(f'Venue {venue_id} was successfully deleted.')

    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    """ Display artists """

    data = db.session.query(Artist).all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    """ Display artist by Id """

    artist = Artist.query.get(artist_id)
    shows = Show.query.filter(Show.artist_id == artist_id)

    past_shows = [{"venue_id": show.venue.id,
                   "venue_name": show.venue.name,
                   "venue_image_link": show.venue.image_link,
                   "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
                   } for show in shows.all() if show.start_time < datetime.today()]

    upcoming_shows = [{"venue_id": show.venue.id,
                       "venue_name": show.venue.name,
                       "venue_image_link": show.venue.image_link,
                       "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
                       } for show in shows.all() if show.start_time > datetime.today()]

    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)

    data = {
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "genres": artist.genres,
        "website_link": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_venue_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }

    return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    """ Search artists by filter """

    search_term = request.form.get('search_term', '')

    artists = Artist.query.filter(
        Artist.name.ilike(
            "%{}%".format(search_term))).all()

    data = [{
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(artist.shows)
    } for artist in artists]

    response = {
        "count": len(artists),
        "data": data
    }

    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    """ Show artist update form """

    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_venue_description
    form.image_link.data = artist.image_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    """ Update an artist """
    
    form_data = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)

    artist.name = form_data.name.data
    artist.city = form_data.city.data
    artist.state = form_data.state.data
    artist.phone = form_data.phone.data
    artist.genres = form_data.genres.data
    artist.website_link = form_data.website_link.data
    artist.facebook_link = form_data.facebook_link.data
    artist.image_link = form_data.image_link.data
    artist.seeking_venue = form_data.seeking_venue.data
    artist.seeking_venue_description = form_data.seeking_description.data

    db.session.commit()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    """ Show venue update form """
    
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    """ Update an venue """

    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.genres = form.genres.data
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.is_seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data

    db.session.commit()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    """ Display new artist form """

    form = ArtistForm()

    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    """ Create an artist """

    form = ArtistForm(request.form)
    artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        genres=form.genres.data,
        phone=form.phone.data,
        website_link=form.website_link.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_venue_description=form.seeking_description.data
    )

    try:
        db.session.add(artist)
        db.session.commit()
        flash(f'Artist {request.form["name"]} was successfully listed!')
        return redirect(url_for('artists'))
    except BaseException:
        flash(
            f'Error occured while trying to create Artist: {request.form["name"]}.')
        return render_template('pages/home.html')
    finally:
        db.session.close()


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    """ Display shows """

    shows = Show.query.all()

    data = [{
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    } for show in shows]

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    """ Display new show form """

    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    """ Create a show """

    form = ShowForm(request.form)
    new_show = Show(
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data
    )

    try:
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
        return redirect(url_for('shows'))
    except BaseException:
        flash(f'Error occured while trying to create Show: {form.name.data}.')
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
