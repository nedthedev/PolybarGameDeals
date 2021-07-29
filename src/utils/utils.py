#!/usr/bin/python3

'''
  Utility functions that are used in main.py. Moved here simply for cleanliness
'''

import argparse

from .db_calls import DB_Calls



''' Scan for arguments to manage the "wishlist" games '''
def check_args():
  parser = argparse.ArgumentParser()
  ''''''
  parser.add_argument("-s", "--silent", help="pass this argument if you want it to run in the background, no rofi window will open", action="store_true")
  ''''''
  parser.add_argument("-b", "--browser", help="specify the path of the browser you want to open links with", default="/usr/bin/firefox")
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
