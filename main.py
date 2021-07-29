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

from src.platforms.pc import PC
from src.platforms.ps import PS
from src.utils.db_calls import  DB_Calls, Tables
from src.utils.utils import get_top_games, check_args
from src.utils.rofi import launch_rofi



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
  top_pc_games = get_top_games(cur, Tables.TOP_PC.value, PC, CUSTOM_UPDATE_DELAY, PC_UPPER_PRICE)
  top_ps_games = get_top_games(cur, Tables.TOP_PS.value, PS, CUSTOM_UPDATE_DELAY)

  ''' totally unnecessary but it looks nice to have width exactly proportional  ''' 
  longest_pc_title = DB_Calls.get_longest_title(cur, Tables.TOP_PC.value)
  longest_ps_title = DB_Calls.get_longest_title(cur, Tables.TOP_PS.value)

  ''' Gather all games into dictionary for convenience '''
  games = {'top_pc_games': top_pc_games, 'top_ps_games': top_ps_games}
  title_lengths = {'longest_pc_title': longest_pc_title, 'longest_ps_title': longest_ps_title} 

  ''' Rofi window logic loop '''
  if(not args.silent):
    if(os.path.exists(args.browser)): launch_rofi(cur, games, title_lengths, args.browser)
    else: print(f"No file at {args.browser}...")

  con.commit()
  con.close()
