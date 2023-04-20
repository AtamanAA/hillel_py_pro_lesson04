import os.path
import sqlite3

from faker import Faker
from faker_music import MusicProvider
from flask import Flask, render_template, request


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/names/")
def names():
    con = sqlite3.connect("first_bd.db")
    cur = con.cursor()
    res = cur.execute("SELECT first_name FROM customers")
    unique_names = set(res.fetchall())
    count_unique_names = len(unique_names)
    count_res = cur.execute("SELECT COUNT(first_name) FROM customers")
    count_customers = count_res.fetchone()[0]
    con.close()

    return render_template('names.html', count_unique_names=count_unique_names, count_customers=count_customers)


@app.route("/tracks/")
def tracks():
    con = sqlite3.connect("first_bd.db")
    cur = con.cursor()
    res = cur.execute("SELECT COUNT(singer) FROM tracks")
    count_tracks = res.fetchone()[0]
    con.close()

    return render_template('tracks.html', count_tracks=count_tracks)


@app.route("/tracks-sec/")
def tracks_sec():
    con = sqlite3.connect("first_bd.db")
    cur = con.cursor()
    res = cur.execute("SELECT singer, song, genre, time FROM tracks")
    all_raw_tracks = res.fetchall()
    con.close()

    def time_to_sec(time_min_sec):
        minutes, seconds = time_min_sec.split(":")
        time_sec = int(minutes) * 60 + int(seconds)
        return time_sec

    all_tracks = []
    for track in all_raw_tracks:
        singer, song, genre, time = track
        all_tracks.append({"singer": singer,
                           "song": song,
                           "genre": genre,
                           "time": time_to_sec(time)})

    return render_template('tracks_sec.html', all_tracks=all_tracks)


@app.route("/add-customers/", methods=['POST', 'GET'])
def add_customers():
    con = sqlite3.connect("first_bd.db")
    cur = con.cursor()

    if request.method == 'POST':
        if not os.path.exists('first_bd.db'):
            cur.execute("CREATE TABLE customers(first_name, last_name, email)")

        count = int(request.form['count'])
        fake = Faker()
        fake_customers = []
        for number in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            fake_customers.append((first_name, last_name, email))

        cur.executemany("INSERT INTO customers VALUES(?, ?, ?)", fake_customers)
        con.commit()
    else:
        count = 10

    res = cur.execute("SELECT first_name, last_name, email FROM customers")
    all_raw_customers = res.fetchall()
    con.close()

    all_customers = []
    for customer in all_raw_customers:
        first_name, last_name, email = customer
        all_customers.append({"first_name": first_name,
                              "last_name": last_name,
                              "email": email})

    return render_template('add_customers.html', all_customers=all_customers, count=count)


@app.route("/add-tracks/", methods=['POST', 'GET'])
def add_tracks():
    con = sqlite3.connect("first_bd.db")
    cur = con.cursor()

    if request.method == 'POST':
        if not os.path.exists('first_bd.db'):
            cur.execute("CREATE TABLE tracks(singer, song, genre, time)")

        count = int(request.form['count'])
        fake = Faker()
        fake.add_provider(MusicProvider)
        fake_tracks = []
        for number in range(count):
            singer = fake.name()
            song = fake.text(max_nb_chars=20).rstrip(".")
            genre = fake.music_genre()
            time = fake.time('%M:%S')
            fake_tracks.append((singer, song, genre, time))

        cur.executemany("INSERT INTO tracks VALUES(?, ?, ?, ?)", fake_tracks)
        con.commit()
    else:
        count = 10

    res = cur.execute("SELECT singer, song, genre, time FROM tracks")
    all_raw_tracks = res.fetchall()
    con.close()

    all_tracks = []
    for track in all_raw_tracks:
        singer, song, genre, time = track
        all_tracks.append({"singer": singer,
                           "song": song,
                           "genre": genre,
                           "time": time})

    return render_template('add_tracks.html', all_tracks=all_tracks, count=count)


if __name__ == "__main__":
    app.run(debug=True)
