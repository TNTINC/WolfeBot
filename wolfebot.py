"""
WolfeBot V2.0
"""
import os
import logging
import sqlite3
from telegram.ext import Updater, CallbackContext, CommandHandler,\
                         MessageHandler, Filters, InlineQueryHandler
from telegram import Update, InlineQueryResultCachedPhoto
import statsd

# Logging
LOG = logging.getLogger()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get our config from the environment
try:
    TOKEN = os.environ["wolfe_token"]
except KeyError:
    LOG.error("Must specify token as environment variable 'wolfe_token'")
    raise KeyError
try:
    DEBUG = os.environ["wolfe_debug"]
except KeyError:
    LOG.warning("wolfe_debug not specified, running in debug mode!!!")
    DEBUG = True
try:
    DBASE = os.environ["wolfe_dbase"]
except KeyError:
    LOG.warning("wolfe_dbase not specified, defaulting to ./wolfe.db")
    DBASE = "./wolfe.db"
try:
    STATSD_ADDRESS = os.environ["wolfe_statsd_address"]
except KeyError:
    LOG.info("wolfe_statsd_address not specified, defaulting to 127.0.0.1")
    STATSD_ADDRESS = "127.0.0.1"
try:
    STATSD_PORT = os.environ["wolfe_statsd_port"]
except KeyError:
    LOG.info("wolfe_statsd_port not specified, defaulting to 8125")
    STATSD_PORT = 8125

# Set up statsd metrics
SD = statsd.StatsClient(STATSD_ADDRESS, STATSD_PORT, prefix="wolfe")

# Set up database connection and access methods
DB = sqlite3.connect(DBASE, check_same_thread=False)

class Image:
    def __init__(self, db_id, file_id, e6_id, url, path, deletes):
        self.db_id = db_id
        self.file_id = file_id
        self.e6_id = e6_id
        self.url = url
        self.path = path
        self.deletes = deletes

@SD.timer("db.read.random_image")
def get_random_image():
    return get_random_images(1)[0]

@SD.timer("db.read.random_images")
def get_random_images(n, cached=False):
    return [Image(*r) for r in DB.execute(
        "SELECT * "+
        "FROM images "+
        ("WHERE file_id != \"\" " if cached else "")+
        "ORDER BY RANDOM() "+
        "LIMIT ?", (n,)).fetchall()]

@SD.timer("db.write.file_id")
def save_file_id(db_id, file_id):
    """ Saves a file_id for an image in the database """
    DB.execute(
        "UPDATE images "
        "SET file_id = ? "
        "WHERE db_id = ? ",
        (file_id, db_id))
    DB.commit()



# Command handlers
@SD.timer("command.yiff")
def yiff(update: Update, context: CallbackContext):
    """ Send random yiff image when yiff mentioned """
    img = get_random_image()
    if img.file_id is not None: # File exists on telegram servers already
        update.message.reply_photo(img.file_id)
        return
    if img.path is not None: # File exists on filesystem, we must get file_id
        with SD.timer("command.yiff.disk"):
            with open("./res/"+img.path, "rb") as f:
                resp = update.message.reply_photo(f)
    elif img.url is not None: # File exists on internet, we must get file_id
        resp = update.message.reply_photo(img.url)
    # resp is message object, contains file_id's for all photo sizes.
    # We get the last one, which is the highest resolution.
    file_id = resp["photo"][-1]["file_id"]
    save_file_id(img.db_id, file_id)


def start(update: Update, context):
    update.message.reply_sticker("BQADAwADAgADZUASA3hbI2mGeTbkAg")
    update.message.reply_html(
        "Hello, welcome to WolfeBot. This bot is not completely stable yet, "
        "so don't be alarmed if it stops working for a bit!\n\n"
        "Bug reports and feature requests ==> "
        "https://github.com/TNTINC/WolfeBot/issues \n"
        "<em>If it goes absolutely haywire, throw a line at</em> @icefla")

@SD.timer("command.inline")
def inline(update: Update, context):
    results = [
        InlineQueryResultCachedPhoto(img.db_id, img.file_id) 
        for img in get_random_images(20, cached=True)
    ]
    update.inline_query.answer(results, next_offset="1")


# Set up the actual bot object
UPDATER = Updater(TOKEN, use_context=True)
for h in [
    CommandHandler('yiff', yiff),
    MessageHandler(Filters.regex(r"^yiff\s*"), yiff),
    
    CommandHandler('start', start),
    CommandHandler('help',  start),

    InlineQueryHandler(inline)
]: UPDATER.dispatcher.add_handler(h)


# Run the bot, polling in debug, webhooks in staging_prod
if DEBUG:
    UPDATER.start_polling()
    UPDATER.idle()
else:
    raise NotImplementedError
