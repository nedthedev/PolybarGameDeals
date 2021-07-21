#!/usr/bin/python3

from datetime import datetime, timedelta
from enum import Enum

class Tables(Enum):
  TOP_PC = "TOP_PC"
  YOUR_PC = "YOUR_PC"
  TOP_PS = "TOP_PS"
  YOUR_PS = "YOUR_PS"
  
class DB_Indices(Enum):
  TITLE = 0
  FULL_PRICE = 1
  SALE_PRICE = 2
  COVER_IMAGE = 3
  URL = 4
  UPDATE_TIME = 5

class DB_Calls:

  _UPDATE_DELAY = timedelta(seconds=0, minutes=0, hours=3, days=0)

  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  @staticmethod
  def get_data(cur, table):
    try:
      return cur.execute(f"""SELECT * FROM {table};""")
    except Exception:
      print(f"Creating table {table}...")
      cur.execute(f"""CREATE TABLE {table}(title TEXT NOT NULL UNIQUE, full_price REAL, sale_price REAL, cover_image TEXT, url TEXT NOT NULL UNIQUE, update_time TEXT);""")
      return cur.execute(f"""SELECT * FROM {table};""").fetchall()

  @staticmethod
  def add_top_deals(cur, table, existing_games, new_games):
    ''' When adding top deals, we need to remove the games that are no longer a "top deal" '''
    unmatched_titles = []
    for existing_game in existing_games:
      matched = False
      for new_game in new_games:
        if(existing_game[DB_Indices.TITLE.value] == new_game['title']):
          matched = True
          break
      if(not matched):
        # append it to the list of titles that we will delete
        unmatched_titles.append(existing_game[DB_Indices.TITLE.value])
    
    ''' Delete the games that aren't found in the api response anymore '''
    for title in unmatched_titles:
      print(f"Removing {title} from top deals...")
      cur.execute(f"""DELETE FROM {table} WHERE TITLE=?""", (title, ))
   
    ''' Update the remainder of the games
        side note: for some reason I couldn't put this cur.execute where I have matched=True??
        It would only do one game... I don't know why... '''
    for game in new_games:
      cur.execute(f"""UPDATE {table} SET sale_price=?, url=?, update_time=? WHERE TITLE=?""", (game['sale_price'], game['url'], datetime.now(), game['title']))



  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  @staticmethod
  def __str_to_dt(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")

  @classmethod
  def __needs_updating(cls, past_time, update_delay=None):
    if(not update_delay):
      update_delay = cls._UPDATE_DELAY
    return ((datetime.now() - past_time) > update_delay)
