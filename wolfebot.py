"""
WolfeBot V2.0
"""
import os
import logging
import sqlite3
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Update
import statsd

# Logging
LOG = logging.getLogger()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

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

@SD.timer("db.read.random_image")
def get_random_image():
    db_id, file_id, e6_id, url, path, deletes = DB.execute(
        "SELECT * "
        "FROM images "
        "ORDER BY RANDOM() "
        "LIMIT 1").fetchone()
    return {"db_id":db_id, "file_id":file_id, "e6_id":e6_id,
            "url":url, "path":path, "deletes":deletes}

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
    if img["file_id"] is not None: # File exists on telegram servers already
        update.message.reply_photo(img["file_id"])
        return
    if img["path"] is not None: # File exists on filesystem, we must get file_id
        with SD.timer("command.yiff.disk"):
            with open("./res/"+img["path"], "rb") as f:
                resp = update.message.reply_photo(f)
    elif img["url"] is not None: # File exists on different server, we must get file_id
        resp = update.message.reply_photo(img["url"])
    # resp is message object, contains file_id's for all photo sizes.
    # We get the last one, which is the highest resolution.
    file_id = resp["photo"][-1]["file_id"]
    save_file_id(img["db_id"], file_id)


# Set up the actual bot object
UPDATER = Updater(TOKEN, use_context=True)

UPDATER.dispatcher.add_handler(CommandHandler('yiff', yiff))
UPDATER.dispatcher.add_handler(MessageHandler(Filters.regex(r"^yiff\s*"), yiff))

# Run the bot, polling in debug, webhooks in staging_prod
if DEBUG:
    UPDATER.start_polling()
    UPDATER.idle()
else:
    raise NotImplementedError
