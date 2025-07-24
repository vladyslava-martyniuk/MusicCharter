from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('musiclibrary.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/musiclibrary")
def music_library():
    conn = get_db_connection()
    music = conn.execute("SELECT * FROM music ORDER BY title ASC").fetchall()
    conn.close()
    return render_template("musiclibrary.html", music=music, search=None)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        artist = request.form.get("artist", "").strip()

        if not title or not artist:
            return "Назва і виконавець — обов'язкові поля.", 400

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO music (title, artist)
            VALUES (?, ?)
        """, (title, artist))
        conn.commit()
        conn.close()
        return redirect(url_for('music_library'))

    return render_template("admin_form.html", book=None, mode="add")

@app.route("/edit/<int:music_id>", methods=["GET", "POST"])
def edit(music_id):
    conn = get_db_connection()
    music_item = conn.execute("SELECT * FROM music WHERE id = ?", (music_id,)).fetchone()
    if music_item is None:
        conn.close()
        return "Музичний запис не знайдено", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        artist = request.form.get("artist", "").strip()

        if not title or not artist:
            return "Назва і виконавець — обов'язкові поля.", 400

        conn.execute("""
            UPDATE music SET title = ?, artist = ?
            WHERE id = ?
        """, (title, artist, music_id))
        conn.commit()
        conn.close()
        return redirect(url_for('music_library'))

    conn.close()
    return render_template("admin_form.html", book=music_item, mode="edit")

@app.route("/delete/<int:music_id>", methods=["POST"])
def delete(music_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM music WHERE id = ?", (music_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('music_library'))

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip().lower()
    conn = get_db_connection()
    music = conn.execute("SELECT * FROM music").fetchall()
    conn.close()
    filtered = [dict(item) for item in music if query in item["title"].lower()]
    return {"results": filtered}

@app.route("/clear-musiclibrary", methods=["POST"])
def clear_music_library():
    conn = get_db_connection()
    conn.execute("DELETE FROM music")
    conn.commit()
    conn.close()
    return redirect(url_for('music_library'))

if __name__ == "__main__":
    app.run(debug=True)

