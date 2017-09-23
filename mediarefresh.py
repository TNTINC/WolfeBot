from glob import glob
from PIL import Image
from os import rename
import sqlite3 as db

con = db.connect('wolfe.db')

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
