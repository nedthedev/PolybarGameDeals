#!/usr/bin/python3
# This scripts fetches game prices for PC and Playstation 4

import json
import requests
import argparse
import sqlite3
from datetime import datetime
from enum import Enum

# an enum class for accessing data from the game tuples
class Index(Enum):
  NAME = 0
  URL = 1
  FULL_PRICE = 2
  SALE_PRICE = 3
  SYSTEM = 4
  TIME = 5

def str_to_dt():
  format = "%Y-%m-%d %H:%M:%S.%f"
  return datetime.strptime(games[0][Index.TIME.value], format).now()

# fetch the deals for the pc games
def fetch_pc_deals(games):
  # https://www.cheapshark.com/api/1.0/games?title='' id lookup for game
  # https://www.cheapshark.com/api/1.0/games?id='' deals for game id
  # https://www.cheapshark.com/api/1.0/deals?upperPrice=10 retrieves deals from the main browse page so long as they're under $10
  url = "https://www.cheapshark.com/api/1.0/games?id="
  return games

# fetch the deals for the playstation games
def fetch_ps_deals(games):
  # https://psprices.com/region-it/game/4194536/cyberpunk-2077 need full url
  return games

# retrieve games from the database
def load_games_list():
  return "loading games"

# check any additional args (add game, delete game)
def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--add-ps", help="add ps games to the database", action="extend", nargs="+")
  parser.add_argument("--del-ps", help="remove ps games from the database", action="extend", nargs="+")
  parser.add_argument("--add-pc", help="add pc games to the database", action="extend", nargs="+")
  parser.add_argument("--del-pc", help="remove pc games from the database", action="extend", nargs="+")
  return parser.parse_args()

# get all the games from the table "GAMES"
def get_game_table(cur):
  tables = cur.execute("""SELECT name FROM sqlite_master WHERE type='table' 
  AND name='GAMES';""").fetchall()
  if(len(tables) == 0):
    cur.execute("""CREATE TABLE GAMES(name TEXT, url TEXT NOT NULL UNIQUE, full_price REAL, sale_price REAL, system TEXT, update_time TEXT);""")
  cur.execute("""SELECT * FROM GAMES;""")
  return cur.fetchall()

# add the list of games provided
def add_games(games, cur):
  for game in games:
    # inject the url and default values into the database
    try:
      cur.execute("""INSERT INTO GAMES VALUES('', ?, 0, 0, '', '')""", (game, ))
    except Exception as err:
      print(err)

# remove the list of games provided
def remove_games(games, cur):
  for game in games:
    # delete the entry with the given url from the database
    try:
      cur.execute("""DELETE FROM GAMES WHERE URL = ?""", (game, ))
    except Exception as err:
      print(err)

if __name__ == "__main__":

  # create a database connection
  con = sqlite3.connect('games.db')
  cur = con.cursor()

  # get the games from the table
  games = get_game_table(cur)

  # initialize args parsing
  args = get_args()

  # collect the games
  arg_games = { }
  arg_games.update({"add_ps": args.add_ps})
  arg_games.update({"remove_ps": args.del_ps})

  # add games if there are any games to add
  if(arg_games['add_ps']):
    add_games(arg_games['add_ps'], cur)
  # remove games if there are any games to remove
  if(arg_games['remove_ps']):
    remove_games(arg_games['remove_ps'], cur)

  # if no database changes were made then update the data
  # this is simply to ensure no redundant, agressive requests
  if(not arg_games['add_ps'] and not arg_games['remove_ps']):
    print("Finding deals...")  

  con.commit()
  con.close()
