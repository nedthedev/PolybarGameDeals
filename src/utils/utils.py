#!/usr/bin/python3

'''
  Utility functions that are used in main.py. Moved here simply for cleanliness
'''

import argparse
from enum import Enum
import subprocess

from .db_calls import DB_Calls, Tables, DB_Indices
from ..platforms.ps import PS



''' Selection enum for picking what platform of games to browse '''
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

''' Returns all the games in the database from the given table and calls methods from cls '''
def get_top_games(cur, table, cls, update_delay=None, upper_price=None):
  if(DB_Calls.needs_updating(cur, table, update_delay)):
    old_top = DB_Calls.get_data(cur, table)
    print(f"Fetching {cls.__name__} deals...")
    new_top = cls.get_top_deals(upper_price)
    DB_Calls.add_top_deals(cur, table, old_top, new_top)
  return DB_Calls.get_data(cur, table)

''' The main rofi logic loop wrapped in a function '''
def launch_rofi(cur, games):
  while(True):
    category = choose_category()
    if(category):
      while(True):
        chosen_game, _table = choose_game(category, games)
        if(chosen_game):
          url = DB_Calls.get_game_url(cur, _table, chosen_game)
          if(url): open_url(url)
          else: break
        else: break
    else: break

''' Rofi window to select what platform of games to browse '''
def choose_category():
  category = subprocess.run(["rofi", "-dmenu", "-p", "Choose category", "-lines", "2", "-columns", "1"], input=str.encode(f"{Categories.TOP_PC.value}{Categories.TOP_PS.value}", encoding="UTF-8"), stdout=subprocess.PIPE)
  if(category.returncode > 0): return None
  else: return category.stdout.decode("UTF-8")

''' Rofi window to select the game you want to see more about '''
def choose_game(category, games):
  _GO_UP = "...Choose Category\n"
  rofi_string = _GO_UP
  if(category == Categories.TOP_PC.value):
    _table = Tables.TOP_PC.value
    for game in games['top_pc_games']:
      rofi_string+=(f"{stretch_string(game[DB_Indices.TITLE.value]):45s} ${game[DB_Indices.SALE_PRICE.value]:.2f}\n")
  elif(category == Categories.TOP_PS.value):
    _table = Tables.TOP_PS.value
    for game in games['top_ps_games']:
      if(game[DB_Indices.SALE_PRICE.value] == PS.ps_plus_price()): rofi_string+=(f"{stretch_string(game[DB_Indices.TITLE.value]):45s} $PS+")
      else: rofi_string+=(f"{stretch_string(game[DB_Indices.TITLE.value]):45s} ${game[DB_Indices.SALE_PRICE.value]:.2f}")
      rofi_string+="\n"
  else: return None, None
  chosen_game = subprocess.run(["rofi", "-dmenu", "-p", "Search game", "-lines", "12", "-columns", "2"], stdout=subprocess.PIPE, input=str.encode(rofi_string, encoding="UTF-8"))
  if(chosen_game.returncode == 0): chosen_game = chosen_game.stdout.decode("UTF-8").split("$")[0].rstrip()
  else: chosen_game = None
  return chosen_game, _table

''' Rofi window confirming whether or not you want to open the link '''
def open_url(url):
  yes = "Yes\n"
  no = "No\n"
  choice = subprocess.run(["rofi", "-dmenu", "-p", f"Open: {url}", "-lines", "2", "-columns", "1"], input=str.encode(f"{yes}{no}", encoding="UTF-8"), stdout=subprocess.PIPE).stdout.decode("UTF-8")
  if(choice == yes): subprocess.run(["firefox", url])

def stretch_string(string, length=None):
  # if(len(string) >= length):
  #   difference = len(string) - length
  #   string = string[:-difference-3] + "..."
  # else:
  #   for _ in range(length-len(string)):
  #     string += " "
  return string