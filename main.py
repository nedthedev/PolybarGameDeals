#!/usr/bin/python3

'''
  This script finds and shows you some of the current best PC and Playstation
  deals. PC deals are found using a public REST API, while all playstation deals
  are scraped from https://psdeals.net/.

  Data Sources:
    All PC Deals are provided using the cheapshark API at https://apidocs.cheapshark.com/. When you select a PC game it will take you to a redirect link as per the
    rules of the api.
    All Playstation deals are scraped from https://psdeals.net/. When you select a Playstation game it will take you to the game's page on the psdeals.net website.
'''

import sqlite3
import os
from datetime import timedelta
import argparse

from src.platforms.pc import PC
from src.platforms.ps import PS
from src.utils.db_calls import  DB_Calls, Tables
from src.utils.rofi import launch_rofi



''' Scan for arguments to manage the "wishlist" games '''
def check_args():
  parser = argparse.ArgumentParser()
  ''''''
  parser.add_argument("-s", "--silent", help="pass this argument if you want it to run in the background, no rofi window will open", action="store_true")
  ''''''
  parser.add_argument("-b", "--browser", help="specify the path of the browser you want to open links with", default="/usr/bin/firefox")
  ''''''
  parser.add_argument("-ps", help="url of game from https://psdeals.net/. Just search for the game you want to add, copy the url, and paste it, along with all other urls, following the -ps argument", action="extend", nargs="+")
  ''''''
  parser.add_argument("-pc", help="id of pc game from https://www.cheapshark.com. To find the id of your game, search for it at https://www.cheapshark.com/api/1.0/games?title=game-name, replacing game-name with your game name, like \"Dishonored 2\". So, then you'd have https://www.cheapshark.com/api/1.0/games?title=Dishonored-2", action="extend", nargs="+")
  ''''''
  return parser.parse_args()

''' Returns all the games in the database from the given table and calls methods from cls '''
def get_games(cur, table, download_games_function, update_delay=None, upper_price=None, ids=None):
  if(DB_Calls.needs_updating(cur, table, update_delay)):
    old_top = DB_Calls.get_data(cur, table)
    new_top = download_games_function(upper_price)
    if(new_top):
      DB_Calls.add_top_deals(cur, table, old_top, new_top)
  return DB_Calls.get_data(cur, table)

#####################
'''   VARIABLES   '''
#####################
CUSTOM_UPDATE_DELAY = None # timedelta(seconds=0, minutes=30, hours=0, days=0)
PC_UPPER_PRICE = 10

######################
'''   MAIN BLOCK   '''
######################
if __name__ == "__main__":
  ''' Move to the current directory '''
  os.chdir(os.path.dirname(__file__))

  ''' Create a cursor and connection for the database interactions '''
  con = sqlite3.connect(f'{os.getcwd()}/games.db')
  cur = con.cursor()

  ''' Check for any arguments '''
  args = check_args()

  ''' Add any new games '''
  # DB_Calls.update_pc_games(cur, args.pc)
  # DB_Calls.update_ps_games(cur, args.ps)

  ''' Update / gather the top games '''
  top_pc_games = get_games(cur, Tables.TOP_PC.value, PC.get_top_deals, CUSTOM_UPDATE_DELAY, PC_UPPER_PRICE)
  top_ps_games = get_games(cur, Tables.TOP_PS.value, PS.get_top_deals, CUSTOM_UPDATE_DELAY)
  pc_wishlist_games = get_games(cur, Tables.PC_WISHLIST.value, PC.get_your_deals, CUSTOM_UPDATE_DELAY, PC_UPPER_PRICE)
  ps_wishlist_games = get_games(cur, Tables.PS_WISHLIST.value, PS.get_your_deals, CUSTOM_UPDATE_DELAY)

  ''' Totally unnecessary but it looks nice to have width exactly proportional  ''' 
  longest_pc_title = DB_Calls.get_longest_title(cur, Tables.TOP_PC.value)
  longest_ps_title = DB_Calls.get_longest_title(cur, Tables.TOP_PS.value)
  longest_pc_wishlist_title = DB_Calls.get_longest_title(cur, Tables.PC_WISHLIST.value)
  longest_ps_wishlist_title = DB_Calls.get_longest_title(cur, Tables.PS_WISHLIST.value)

  ''' Gather all games into dictionary for convenience '''
  games = {Tables.TOP_PC.value: top_pc_games, Tables.TOP_PS.value: top_ps_games, Tables.PC_WISHLIST.value: pc_wishlist_games, Tables.PS_WISHLIST.value: ps_wishlist_games}
  title_lengths = {'longest_top_pc_title': longest_pc_title, 'longest_top_ps_title': longest_ps_title, 'longest_pc_wishlist_title': longest_pc_wishlist_title, 'longest_ps_wishlist_title': longest_ps_wishlist_title} 

  ''' Rofi window logic loop '''
  if(not args.silent):
    if(os.path.exists(args.browser)): launch_rofi(cur, games, title_lengths, args.browser)
    else: print(f"No file at {args.browser}...")

  con.commit()
  con.close()
