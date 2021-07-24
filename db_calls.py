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

  _UPDATE_DELAY = timedelta(seconds=0, minutes=0, hours=1, days=0)

  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  @staticmethod
  def get_data(cur, table):
    try:
      cur.execute(f"""SELECT SALE_PRICE FROM {table}""")
    except Exception:
      cur.execute(f"""CREATE TABLE {table}(title TEXT NOT NULL UNIQUE, full_price REAL, sale_price REAL, cover_image TEXT, url TEXT NOT NULL UNIQUE, update_time TEXT, title_length INTEGER);""")
    return cur.execute(f"""SELECT * FROM {table} ORDER BY sale_price ASC""").fetchall()

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
      cur.execute(f"""DELETE FROM {table} WHERE TITLE=?""", (title, ))
   
    ''' Update the remainder of the games
        side note: for some reason I couldn't put this cur.execute where I have matched=True??
        It would only do one game... I don't know why... '''
    for game in new_games: 
      if(cur.execute(f"SELECT * FROM {table} WHERE TITLE=?", (game['title'], )).fetchone()):
        cur.execute(f"""UPDATE {table} SET sale_price=?, url=?, update_time=? WHERE TITLE=?""", (game['sale_price'], game['url'], datetime.now(), game['title']))
      else:
        cur.execute(f"""INSERT INTO {table} VALUES(?, ?, ?, ?, ?, ?, ?)""", (game['title'], game['full_price'], game['sale_price'], game['cover_image'], game['url'], datetime.now(), len(game['title'])))

  @staticmethod
  def get_longest_title(cur, table):
    return cur.execute(f"""SELECT title_length FROM {table} ORDER BY title_length DESC""").fetchone()

  @staticmethod
  def get_game_url(cur, table, title):
    return cur.execute(f"""SELECT url FROM {table} WHERE TITLE=?""", (title, )).fetchone()[0]

  @classmethod
  def needs_updating(cls, cur, table, update_delay=None):
    try:  # attempt to get the first game's update time
      game = cur.execute(f"""SELECT * FROM {table};""").fetchone()
      past_time = cls.__str_to_dt(game[DB_Indices.UPDATE_TIME.value])
    except: # the table must be empty
      return True
    if(not update_delay):
      update_delay = cls._UPDATE_DELAY
    return ((datetime.now() - past_time) > update_delay)

  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  @staticmethod
  def __str_to_dt(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
