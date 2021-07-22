#!/usr/bin/python3

''' 

'''

import argparse
import sqlite3
from datetime import timedelta

from pc import PC
from ps import PS
from db_calls import DB_Calls, Tables, DB_Indices

''' Scan for arguments to manage the "wishlist" games '''
def check_args():
  parser = argparse.ArgumentParser()
  ''''''
  parser.add_argument("-ps", help="id of game from https://psdeals.net/. To find the id of your game, search for it and take the id from the url which looks like this: https://psdeals.net/.../game/{ID}/game-name. For instance, the url for Dishonored 2 is https://psdeals.net/us-store/game/884376/dishonored-2 and the id is 884376.", action="extend", nargs="+")
  ''''''
  parser.add_argument("-pc", help="id of pc game from https://www.cheapshark.com. To find the id of your game, search for it at https://www.cheapshark.com/api/1.0/games?title=game-name, replacing game-name with your game name, like \"Dishonored 2\". So, then you'd have https://www.cheapshark.com/api/1.0/games?title=Dishonored-2", action="extend", nargs="+")
  ''''''
  return parser.parse_args()

if __name__ == "__main__":

  CUSTOM_UPDATE_DELAY = timedelta(seconds=0, minutes=30, hours=0, days=0)

  ''' Create a cursor and connection for the database interactions '''
  con = sqlite3.connect('games.db')
  cur = con.cursor()

  ''' Check for any arguments '''
  args = check_args()

  ''' Add any new games '''
  # DB_Calls.update_pc_games(cur, args.pc)
  # DB_Calls.update_ps_games(cur, args.ps)

  ''' There are 4 steps to take for each "collection" of games '''
  if(DB_Calls.needs_updating(cur, Tables.TOP_PC.value)):
    old_top_pc = DB_Calls.get_data(cur, Tables.TOP_PC.value) # Get current database data
    new_top_pc = PC.get_top_deals() # Get the deals
    DB_Calls.add_top_deals(cur, Tables.TOP_PC.value, old_top_pc, new_top_pc) # Update the database
  top_pc_games = DB_Calls.get_data(cur, Tables.TOP_PC.value) # Gather the data from the database

  ''' Repeat the process for each "collection" of games '''
  if(DB_Calls.needs_updating(cur, Tables.TOP_PS.value)):
    old_top_ps = DB_Calls.get_data(cur, Tables.TOP_PS.value)
    new_top_ps = PS.get_top_deals()
    DB_Calls.add_top_deals(cur, Tables.TOP_PS.value, old_top_ps, new_top_ps)
  top_ps_games = DB_Calls.get_data(cur, Tables.TOP_PS.value)

  ''' Format the data to pretty printed for the rofi popup '''
  for game in top_pc_games:
    print(f"{game[DB_Indices.TITLE.value]:47s} ${game[DB_Indices.SALE_PRICE.value]:.2f}")

  con.commit()
  con.close()

  exit()
