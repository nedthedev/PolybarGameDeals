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
from src.utils.db_enums import DB_Tables
from src.utils.db_calls import DB_Calls
from src.utils.rofi import launch_rofi
from src.platforms.ps import PS



#####################
'''   VARIABLES   '''
#####################
''' The amount of time that must pass before updating the database. Default is 12 hours '''
CUSTOM_UPDATE_DELAY = None # timedelta(seconds=0, minutes=0, hours=2, days=0)
''' The maximum price for the PC deals you want to find '''
PC_UPPER_PRICE = 10

''' Scan for arguments to manage the "wishlist" games '''
def check_args():
  parser = argparse.ArgumentParser()
  ''''''
  parser.add_argument("-r", "--rofi", help="run rofi window exclusively, do not check for updates, just open the rofi window", action="store_true")
  ''''''
  parser.add_argument("-s", "--silent", help="update games if necessary, pass this argument if you don't want a rofi window to open", action="store_true")
  ''''''
  parser.add_argument("-b", "--browser", help="specify the path of the browser you want to open links with", default="/usr/bin/firefox")
  ''''''
  parser.add_argument("-ps", help="url of game from https://psdeals.net/. Just search for the game you want to add, copy the url, and paste it, along with all other urls, following the -ps argument", action="extend", nargs="+")
  ''''''
  parser.add_argument("-pc", help="id of pc game from https://www.cheapshark.com. To find the id of your game, search for it at https://www.cheapshark.com/api/1.0/games?title=game-name, replacing game-name with your game name, like \"Dishonored 2\". So, then you'd have https://www.cheapshark.com/api/1.0/games?title=Dishonored-2", action="extend", nargs="+")
  ''''''
  return parser.parse_args()

''' A generic function for updating wishlist games '''
def update_wishlist_games(cur, table, find_outdated_games_function, update_function, wishlist_args):
  ''' Figure out which wishlist games need updating '''
  outdated_games = find_outdated_games_function(cur, table)

  ''' Fetch deals for new and existing wishlist games  '''
  if(wishlist_args or outdated_games):
    outdated_games += wishlist_args
    update_function(cur, table, outdated_games)

''' A generic function for updating top game deals '''
def update_top_games(cur, table, download_games_function, update_delay=None, upper_price=None):
  if(DB_Calls.needs_updating(cur, table, update_delay)):
    old_top = DB_Calls.get_data(cur, table)
    new_top = download_games_function(upper_price)
    if(new_top):
      DB_Calls.add_top_deals(cur, table, old_top, new_top)



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

  ''' Remove any arguments that are already in the database 
      If they need updating they will be found later ''' 
  if(args.pc): 
    for index, id in enumerate(args.pc):
      if(DB_Calls.game_exists(cur, DB_Tables.PC_WISHLIST.value, PC, id)):
        del args.pc[index]
  else: args.pc = []
  if(args.ps):
    for index, url in enumerate(args.ps):
      if(DB_Calls.game_exists(cur, DB_Tables.PS_WISHLIST.value, PS, url)):
        del args.ps[index]
  else: args.ps = []
  
  ''' If we did not pass the -r option then check for updates '''
  if(not args.rofi):
    ''' update the top games '''
    update_top_games(cur, DB_Tables.TOP_PC.value, PC.get_top_deals, CUSTOM_UPDATE_DELAY, PC_UPPER_PRICE)
    update_top_games(cur, DB_Tables.TOP_PS.value, PS.get_top_deals, CUSTOM_UPDATE_DELAY)
    ''' update wishlist games '''
    update_wishlist_games(cur, DB_Tables.PC_WISHLIST.value, DB_Calls.pc_wishlist_needs_updating, DB_Calls.add_pc_games, args.pc)
    update_wishlist_games(cur, DB_Tables.PS_WISHLIST.value, DB_Calls.ps_wishlist_needs_updating, DB_Calls.add_ps_games, args.ps)

  ''' Get games from the database '''
  pc_wishlist_games = DB_Calls.get_data(cur, DB_Tables.PC_WISHLIST.value)
  ps_wishlist_games = DB_Calls.get_data(cur, DB_Tables.PS_WISHLIST.value)
  top_pc_games = DB_Calls.get_data(cur, DB_Tables.TOP_PC.value)
  top_ps_games = DB_Calls.get_data(cur, DB_Tables.TOP_PS.value)

  ''' Totally unnecessary but it looks nice to have rofi titles equal  ''' 
  longest_top_pc_title = DB_Calls.get_longest_title(cur, DB_Tables.TOP_PC.value)
  longest_top_ps_title = DB_Calls.get_longest_title(cur, DB_Tables.TOP_PS.value)
  longest_pc_wishlist_title = DB_Calls.get_longest_title(cur, DB_Tables.PC_WISHLIST.value)
  longest_ps_wishlist_title = DB_Calls.get_longest_title(cur, DB_Tables.PS_WISHLIST.value)

  ''' Gather all games into dictionary for convenience '''
  games = {
    DB_Tables.TOP_PC.value: top_pc_games, 
    DB_Tables.TOP_PS.value: top_ps_games, 
    DB_Tables.PC_WISHLIST.value: pc_wishlist_games, 
    DB_Tables.PS_WISHLIST.value: ps_wishlist_games
  }
  title_lengths = {
    DB_Tables.TOP_PC.value: longest_top_pc_title, 
    DB_Tables.TOP_PS.value: longest_top_ps_title, 
    DB_Tables.PC_WISHLIST.value: longest_pc_wishlist_title, 
    DB_Tables.PS_WISHLIST.value: longest_ps_wishlist_title
  } 

  ''' Rofi window logic loop '''
  if(args.rofi or not args.silent):
    if(os.path.exists(args.browser)): launch_rofi(cur, games, title_lengths, args.browser)
    else: print(f"No file at {args.browser}...")
  
  con.commit()
  con.close()
