from mongoengine import *

from data_retrieve_utils import populate_us_symbols_in_db, populate_key_stats

DB_NAME = 'fin_data'
KEY_STATS_GAP_DAYS = 30

connect(DB_NAME)

populate_us_symbols_in_db()
populate_key_stats(KEY_STATS_GAP_DAYS)

disconnect()