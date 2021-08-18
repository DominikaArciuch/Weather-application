import sys
import requests
from sqlalchemy.exc import IntegrityError
import base
import os
from api import google_api, weather_api
from flask import render_template, request, redirect, url_for, flash


def get_city_photo(city, nr):
    r = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json?input={}&inputtype=textquery&key={}".format(
            city, google_api))
    photo_ref = r.json()["results"][0]["photos"][0]["photo_reference"]
    r = requests.get(
        "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxheight=500".format(
            google_api, photo_ref))
    photo = open(f"./static/img/city{nr}.jpg", "wb")
    for chunk in r:
        if chunk:
            photo.write(chunk)
    photo.close()


@base.app.route('/')
def index():
    city_info = []
    for i, city in enumerate(base.City.query.all()):
        city_id = city.id
        city = city.name
        if not os.path.exists(f"./static/img/{city_id}.jpg"):
            get_city_photo(city, city_id)
        r = requests.get(
            "http://api.openweathermap.org/data/2.5/weather?appid={}&q={}".format(weather_api, city))

        temp = round(r.json()["main"]["temp"] - 273.15)
        weather_state = r.json()["weather"][0]["description"]
        weather_icon = r.json()["weather"][0]["icon"]
        dict_with_weather_info = {"city": city, "state": weather_state, "temp": temp, "city_id": city_id, "icon": weather_icon}
        city_info.append(dict_with_weather_info)
    return render_template('index.html', city_info=city_info)


@base.app.route('/delete', methods=['POST'])
def delete():
    city_id = request.form["id"]
    os.remove(f"./static/img/city{city_id}.jpg")
    city = base.City.query.filter_by(id=city_id).first()
    base.db.session.delete(city)
    base.db.session.commit()
    return redirect(url_for('index'))


@base.app.route('/', methods=['POST'])
def add_city():
    city = request.form['city_name']
    r = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?appid={}&q={}".format(weather_api, city))
    if r.json()["cod"] == 200:
        try:
            new_city = base.City(name=city)
            base.db.session.add(new_city)
            base.db.session.commit()
        except IntegrityError:
            flash('The city has already been added to the list!')
    else:
        flash("The city doesn't exist!")
    return redirect(url_for('index'))


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        base.app.run(host=arg_host, port=arg_port)
    else:
        base.app.run()
