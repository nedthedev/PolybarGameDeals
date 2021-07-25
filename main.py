#!/usr/bin/python3

'''
  This script finds and shows you some of the current best PC and Playstation
  deals. PC deals are found using a public REST API, while all playstation deals
  are scraped from https://psdeals.net/ using Python.

  Data Sources:
    All PC Deals are provided using the cheapshark API at https://apidocs.cheapshark.com/. When you select a PC game it will take you to a redirect link as per the
    rules of the api.
    All Playstation deals are scraped from https://psdeals.net/. When you select a 
    Playstation game it will take you to the game's page on the psdeals.net website.
'''

import argparse
from enum import Enum
import sqlite3
from datetime import timedelta
import subprocess

from pc import PC
from ps import PS
from db_calls import DB_Calls, Tables, DB_Indices

class Categories(Enum):
  TOP_PS = "Top Playstation Deals\n"
  TOP_PC = "Top PC Deals\n"

''' Scan for arguments to manage the "wishlist" games '''
def check_args():
  parser = argparse.ArgumentParser()
  ''''''
  parser.add_argument("-ps", help="id of game from https://psdeals.net/. To find the id of your game, search for it and take the id from the url which looks like this: https://psdeals.net/.../game/{ID}/game-name. For instance, the url for Dishonored 2 is https://psdeals.net/us-store/game/884376/dishonored-2 and the id is 884376.", action="extend", nargs="+")
  ''''''
  parser.add_argument("-pc", help="id of pc game from https://www.cheapshark.com. To find the id of your game, search for it at https://www.cheapshark.com/api/1.0/games?title=game-name, replacing game-name with your game name, like \"Dishonored 2\". So, then you'd have https://www.cheapshark.com/api/1.0/games?title=Dishonored-2", action="extend", nargs="+")
  ''''''
  return parser.parse_args()

def choose_category():
  category = subprocess.run(["rofi", "-dmenu", "-p", "Choose category", "-lines", "2", "-columns", "1"], input=str.encode(f"{Categories.TOP_PC.value}{Categories.TOP_PS.value}", encoding="UTF-8"), stdout=subprocess.PIPE)
  if(category.returncode > 0): return None
  else: return category.stdout.decode("UTF-8")

def choose_game(category):
  rofi_string = _GO_UP
  if(category == Categories.TOP_PC.value):
    _table = Tables.TOP_PC.value
    for game in top_pc_games:
      rofi_string+=(f"{game[DB_Indices.TITLE.value]:45s} ${game[DB_Indices.SALE_PRICE.value]:.2f}\n")
  elif(category == Categories.TOP_PS.value):
    _table = Tables.TOP_PS.value
    for game in top_ps_games:
      if(game[DB_Indices.SALE_PRICE.value] == PS.ps_plus_price()): rofi_string+=(f"{game[DB_Indices.TITLE.value]:45s} $ PS+")
      else: rofi_string+=(f"{game[DB_Indices.TITLE.value]:45s} ${game[DB_Indices.SALE_PRICE.value]:.2f}")
      rofi_string+="\n"
  else: return None, None
  chosen_game = subprocess.run(["rofi", "-dmenu", "-p", "Search game", "-lines", "12", "-columns", "2"], stdout=subprocess.PIPE, input=str.encode(rofi_string, encoding="UTF-8"))
  if(chosen_game.returncode == 0): chosen_game = chosen_game.stdout.decode("UTF-8").split("$")[0].rstrip()
  else: chosen_game = None
  return chosen_game, _table



######################
'''   MAIN BLOCK   '''
######################
if __name__ == "__main__":

  CUSTOM_UPDATE_DELAY = None # timedelta(seconds=0, minutes=30, hours=0, days=0)
  PC_UPPER_PRICE = 10

  # this is an option for the user to go back up to select pc or playstation deals
  _GO_UP = "..Choose Category\n"

  ''' Create a cursor and connection for the database interactions '''
  con = sqlite3.connect('games.db')
  cur = con.cursor()

  ''' Check for any arguments '''
  # args = check_args()

  ''' Add any new games '''
  # DB_Calls.update_pc_games(cur, args.pc)
  # DB_Calls.update_ps_games(cur, args.ps)

  ''' SOME NEARLY DUPLICATE CODE :nauseated_face: '''
  ''' Update / gather the PC games '''
  if(DB_Calls.needs_updating(cur, Tables.TOP_PC.value, CUSTOM_UPDATE_DELAY)):
    old_top_pc = DB_Calls.get_data(cur, Tables.TOP_PC.value)
    new_top_pc = PC.get_top_deals(PC_UPPER_PRICE)
    DB_Calls.add_top_deals(cur, Tables.TOP_PC.value, old_top_pc, new_top_pc)
  top_pc_games = DB_Calls.get_data(cur, Tables.TOP_PC.value)

  ''' Update / gather the Playstation games '''
  if(DB_Calls.needs_updating(cur, Tables.TOP_PS.value, CUSTOM_UPDATE_DELAY)):
    old_top_ps = DB_Calls.get_data(cur, Tables.TOP_PS.value)
    new_top_ps = PS.get_top_deals()
    DB_Calls.add_top_deals(cur, Tables.TOP_PS.value, old_top_ps, new_top_ps)
  top_ps_games = DB_Calls.get_data(cur, Tables.TOP_PS.value)

  ''' Rofi window logic loop '''
  while(True):
    category = choose_category()
    if(category):
      while(True):
        chosen_game, _table = choose_game(category)
        if(chosen_game):
          url = DB_Calls.get_game_url(cur, _table, chosen_game)
          if(url): subprocess.run(["firefox", url])
          else: break
        else: break
    else: break

  con.commit()
  con.close()
  exit()
