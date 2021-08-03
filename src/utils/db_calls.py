#!/usr/bin/python3

'''
  This script contains all the methods pertaining to database interactions.
  ps.py and pc.py both fetch and return the data that this file processes and
  adds to the database.
'''

from datetime import datetime, timedelta
from enum import Enum

class Tables(Enum):
  TOP_PC = "TOP_PC"
  PC_WISHLIST = "PC_WISHLIST"
  TOP_PS = "TOP_PS"
  PS_WISHLIST = "PS_WISHLIST"
  
class DB_Indices(Enum):
  TITLE = 0
  FULL_PRICE = 1
  SALE_PRICE = 2
  COVER_IMAGE = 3
  URL = 4
  UPDATE_TIME = 5

class DB_Calls:
  #####################
  '''   VARIABLES   '''
  #####################
  ''' The default delay before updating the top deals '''
  _UPDATE_DELAY = timedelta(seconds=0, minutes=0, hours=1, days=0)



  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  ''' A simple function to fetch all the data from the given table. If the table
      doesn't exist then it will be created.
  '''
  @staticmethod
  def get_data(cur, table):
    try:
      cur.execute(f"""SELECT SALE_PRICE FROM {table}""")
    except Exception:
      cur.execute(f"""CREATE TABLE {table}(title TEXT NOT NULL UNIQUE, full_price REAL, sale_price REAL, cover_image TEXT, url TEXT NOT NULL UNIQUE, update_time TEXT, title_length INTEGER)""")
    return cur.execute(f"""SELECT * FROM {table} ORDER BY sale_price ASC""").fetchall()

  ''' Add top deals to the database. Since top deals will time out and not exist
      anymore, we need to check if games in the database need to updated or
      removed.
  '''
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
        ''' append it to the list of titles that we will delete '''
        unmatched_titles.append(existing_game[DB_Indices.TITLE.value])
    
    ''' Delete the games that aren't found in the api response anymore '''
    for title in unmatched_titles:
      DB_Calls.delete_game(cur, table, title)
   
    ''' Update the remainder of the games that are already present, add the
        games that are new entries to the database.
    '''
    for game in new_games: 
      if(cur.execute(f"SELECT * FROM {table} WHERE TITLE=?", (game['title'], )).fetchone()):
        cur.execute(f"""UPDATE {table} SET sale_price=?, url=?, update_time=? WHERE TITLE=?""", (game['sale_price'], game['url'], datetime.now(), game['title']))
      else:
        cur.execute(f"""INSERT INTO {table} VALUES(?, ?, ?, ?, ?, ?, ?)""", (game['title'], game['full_price'], game['sale_price'], game['cover_image'], game['url'], datetime.now(), len(game['title'])))

  @staticmethod
  def delete_game(cur, table, title):
    cur.execute(f"""DELETE FROM {table} WHERE TITLE=?""", (title, ))

  @staticmethod
  def delete_game_now(cur, table, title, games):
    for index, game in enumerate(games[table]):
      if(game[DB_Indices.TITLE.value] == title):
        del games[table][index]
        cur.execute(f"""DELETE FROM {table} WHERE TITLE=?""", (title, ))
        return games

  ''' Fetch a game's url given the title and table of the game '''
  @staticmethod
  def get_game_url(cur, table, title):
    url = cur.execute(f"""SELECT url FROM {table} WHERE TITLE=?""", (title, )).fetchone()
    if(url): return url[0]
    else: return None

  ''' Simple function to get the longest title from the given table '''
  @staticmethod
  def get_longest_title(cur, table):
    length = cur.execute(f"""SELECT title_length FROM {table} ORDER BY title_length DESC""").fetchone()
    if(length): 
      if(length[0] > 40): return length[0]
    return 40

  ''' Determine if the top deals need to be updated based on update_delay. The 
      function first checks to see if an entry even exists, if one does then it
      will check the elapsed time.
  '''
  @staticmethod
  def needs_updating(cur, table, update_delay=None):
    try: past_time = DB_Calls.__str_to_dt(cur.execute(f"""SELECT update_time FROM {table}""").fetchone()[0])
    except: return True
    if(not update_delay):
      update_delay = DB_Calls._UPDATE_DELAY
    return ((datetime.now() - past_time) > update_delay)



  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  @staticmethod
  def __str_to_dt(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
