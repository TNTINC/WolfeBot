from glob import glob
from PIL import Image
from os import rename
import sqlite3 as db

con = db.connect('wolfe.db')

# Create the media table if it does not exist.
con.execute("""CREATE TABLE IF NOT EXISTS "media" (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`tg_id`	TEXT,
	`path`	INTEGER NOT NULL UNIQUE,
	`filetype`	TEXT NOT NULL,
	`approved`	INTEGER NOT NULL DEFAULT 1,
	`type`	TEXT NOT NULL DEFAULT 'yiff',
	`check`	INTEGER NOT NULL DEFAULT 1
);""")
con.commit()

RES_FOLDER = 'res/'

data = []

for f in glob('%s*/*.*' % RES_FOLDER):
	fn = f[len(RES_FOLDER):]

	fold, fnam = fn.split('/')
	fnam, ext = fnam.rsplit('.', 1)

	if ext not in ['jpg', 'jpeg', 'png', 'gif']:
		continue
		print('Skipping %s' % fn) 

	print(fold,fnam,ext)

	try:
		im = Image.open(f)
	except:
		print('Can\'t open %s' % fn)
		rename(f, '%s_broken' % f)
		continue

	data += [(fn, ext)] 

con.executemany("INSERT OR IGNORE INTO media (path, filetype) VALUES (?,?)", data)
con.commit()
