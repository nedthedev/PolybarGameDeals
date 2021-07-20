#!/usr/bin/python3

''' 

'''

import argparse
import sqlite3

from pc import PC
from ps import PS
from db_calls import DB_Calls, Tables

''' Scan for arguments to manage the "wishlist" games '''
def check_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-ps", help="id of game from https://psdeals.net/. To find the id of your game, search for it and take the id from the url which looks like this: https://psdeals.net/.../game/{ID}/game-name. For instance, the url for Dishonored 2 is https://psdeals.net/us-store/game/884376/dishonored-2 and the id is 884376.", action="extend", nargs="+")
  parser.add_argument("-pc", help="id of pc game from https://www.cheapshark.com. To find the id of your game, search for it at https://www.cheapshark.com/api/1.0/games?title=game-name, replacing game-name with your game name, like \"Dishonored 2\". So, then you'd have https://www.cheapshark.com/api/1.0/games?title=Dishonored-2", action="extend", nargs="+")
  return parser.parse_args()

if __name__ == "__main__":
  ''' Create a cursor and connection for the database interactions '''
  con = sqlite3.connect('games.db')
  cur = con.cursor()

  ''' Check for any arguments '''
  args = check_args()

  ''' Add any new games '''
  # DB_Calls.update_pc_games(cur, args.pc)
  # DB_Calls.update_ps_games(cur, args.ps)

  ''' Get current database data and check if it needs updating '''
  top_pc = DB_Calls.get_data(cur, Tables.TOP_PC.value)
  your_pc = DB_Calls.get_data(cur, Tables.YOUR_PC.value)
  top_ps = DB_Calls.get_data(cur, Tables.TOP_PS.value)
  your_ps = DB_Calls.get_data(cur, Tables.YOUR_PS.value)

  ''' Get the deals '''
  # pc_games = PC.get_top_deals()
  ps_games = PS.get_top_deals()

  ''' Update the database '''
  # commit the freshly parsed data
  # for game in pc_games:
  #   DB_Calls.add_data(cur, Tables.TOP_PC.value, game)
  for game in ps_games:
    DB_Calls.add_data(cur, Tables.TOP_PS.value, game)

  ''' Gather the data from the database '''
  # fetch the relevant data for rendering

  ''' Format the data to pretty printed for the rofi popup '''
  # print out the data to the bash script

  con.commit()
  con.close()

  exit()
