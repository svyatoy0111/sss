# файл: steam_site.py
from flask import Flask, redirect, url_for, session, request, render_template_string
from flask_session import Session
from requests_steam import SteamOpenID
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

STEAM_OPENID = SteamOpenID(realm="http://localhost:5000", return_url="http://localhost:5000/authorize")

# Простая форма для ввода Discord ID
HTML_FORM = """
<h2>Привязка Steam к Discord</h2>
<form action="/login">
  Ваш Discord ID: <input name="discord_id" required>
  <button type="submit">Войти через Steam</button>
</form>
"""

@app.route("/")
def index():
    return render_template_string(HTML_FORM)

@app.route("/login")
def login():
    discord_id = request.args.get("discord_id")
    if not discord_id:
        return "Discord ID обязателен!"
    session["discord_id"] = discord_id
    return redirect(STEAM_OPENID.url)

@app.route("/authorize")
def authorize():
    steam_id = STEAM_OPENID.validate(request.args)
    if not steam_id:
        return "Ошибка авторизации через Steam!"
    discord_id = session.get("discord_id")
    # Сохраняем связку в базу данных
    conn = sqlite3.connect("steam_links.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS steam_links (
            discord_id INTEGER PRIMARY KEY,
            steam_url TEXT
        )
    """)
    steam_url = f"https://steamcommunity.com/profiles/{steam_id}"
    cursor.execute(
        "INSERT OR REPLACE INTO steam_links (discord_id, steam_url) VALUES (?, ?)",
        (discord_id, steam_url)
    )
    conn.commit()
    conn.close()
    return f"Успешно! Ваш Discord ID: {discord_id}, ваш Steam профиль: <a href='{steam_url}'>{steam_url}</a>"