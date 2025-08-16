from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///musiclibrary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Моделі
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    songs = db.relationship('Song', back_populates='artist', cascade='all, delete-orphan')

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    artist = db.relationship('Artist', back_populates='songs')

# Ініціалізація БД

with app.app_context():
    db.create_all()
    print("База даних та таблиці успішно створені ✅")



# Головна сторінка
@app.route("/")
def home():
    return render_template("index.html")

# Всі пісні
@app.route("/musiclibrary")
def music_library():
    songs = Song.query.order_by(Song.title.asc()).all()
    return render_template("musiclibrary.html", songs=songs)

# Додавання виконавця
@app.route("/admin/artist", methods=["GET", "POST"])
def add_artist():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return "Назва виконавця обов'язкова", 400
        db.session.add(Artist(name=name))
        db.session.commit()
        return redirect(url_for('music_library'))
    return render_template("artist_form.html", mode="add", artist=None)

# Додавання пісні
@app.route("/admin/song", methods=["GET", "POST"])
def add_song():
    artists = Artist.query.all()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        artist_id = request.form.get("artist_id")
        if not title or not artist_id:
            return "Назва пісні та виконавець обов'язкові", 400
        db.session.add(Song(title=title, artist_id=int(artist_id)))
        db.session.commit()
        return redirect(url_for('music_library'))
    return render_template("song_form.html", mode="add", song=None, artists=artists)

# Редагування пісні
@app.route("/edit/song/<int:song_id>", methods=["GET", "POST"])
def edit_song(song_id):
    song = Song.query.get_or_404(song_id)
    artists = Artist.query.all()
    if request.method == "POST":
        song.title = request.form.get("title", "").strip()
        song.artist_id = int(request.form.get("artist_id"))
        db.session.commit()
        return redirect(url_for('music_library'))
    return render_template("song_form.html", mode="edit", song=song, artists=artists)

# Видалення пісні
@app.route("/delete/song/<int:song_id>", methods=["POST"])
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('music_library'))

# Видалення виконавця
@app.route("/delete/artist/<int:artist_id>", methods=["POST"])
def delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    db.session.delete(artist)
    db.session.commit()
    return redirect(url_for('music_library'))

# Пошук пісень
@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip().lower()
    results = Song.query.filter(Song.title.ilike(f"%{query}%")).all()
    return {"results": [{"id": s.id, "title": s.title, "artist": s.artist.name} for s in results]}

if __name__ == "__main__":
    app.run(debug=True)