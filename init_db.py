from mongoengine import *

from data_retrieve_utils import populate_us_symbols_in_db, populate_key_stats

DB_NAME = 'fin_data'

connect(DB_NAME)

# populate_us_symbols_in_db()
populate_key_stats()

disconnect()