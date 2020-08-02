"""
Grab some popular posts from e621 and add them to the database.
"""
import os
import sqlite3
import requests

DBASE = os.environ["wolfe_dbase"]
DB = sqlite3.connect(DBASE)

# Set up table
DB.execute("""CREATE TABLE IF NOT EXISTS images (
    db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT,
    e6_id TEXT,
    url TEXT,
    path TEXT,
    deletes INT DEFAULT 0,
    UNIQUE(url, e6_id),
    UNIQUE(path)
)
""")

# Grab popular posts from e621
req = requests.get("https://e621.net/posts.json?tags=order%3Arank+m%2Fm",
                   headers={"user-agent":"wolfe-url-fetcher"})
posts = []
for post in req.json()["posts"]:
    print(post["file"]["url"])
    if post["file"]["url"] is not None: # Standard blacklist
        if post["file"]["size"] < 5242880: # Telegram only accepts images of size<5Mb
            posts.append((post["id"], post["file"]["url"]))
DB.executemany("INSERT OR IGNORE INTO images (e6_id,url) VALUES (?,?)", posts)
DB.commit()
