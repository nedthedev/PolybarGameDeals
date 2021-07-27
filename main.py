#!/usr/bin/python3

'''
  This script finds and shows you some of the current best PC and Playstation
  deals. PC deals are found using a public REST API, while all playstation deals
  are scraped from https://psdeals.net/ using Python.

  Data Sources:
    All PC Deals are provided using the cheapshark API at https://apidocs.cheapshark.com/. When you select a PC game it will take you to a redirect link as per the
    rules of the api.
    All Playstation deals are scraped from https://psdeals.net/. When you select a Playstation game it will take you to the game's page on the psdeals.net website.
'''

import sqlite3
from datetime import timedelta

from pc import PC
from ps import PS
from db_calls import  Tables
from utils import get_top_games, launch_rofi, check_args



#####################
'''   VARIABLES   '''
#####################
CUSTOM_UPDATE_DELAY = None # timedelta(seconds=0, minutes=30, hours=0, days=0)
PC_UPPER_PRICE = 10

######################
'''   MAIN BLOCK   '''
######################
if __name__ == "__main__":
  ''' Create a cursor and connection for the database interactions '''
  con = sqlite3.connect('games.db')
  cur = con.cursor()

  ''' Check for any arguments '''
  # args = check_args()

  ''' Add any new games '''
  # DB_Calls.update_pc_games(cur, args.pc)
  # DB_Calls.update_ps_games(cur, args.ps)

  ''' Update / gather the PC games '''
  top_pc_games = get_top_games(cur, Tables.TOP_PC.value, PC, CUSTOM_UPDATE_DELAY, PC_UPPER_PRICE)
  
  ''' Update / gather the Playstation games '''
  top_ps_games = get_top_games(cur, Tables.TOP_PS.value, PS, CUSTOM_UPDATE_DELAY)  

  ''' Gather all games into dictionary for convenience '''
  games = {'top_pc_games': top_pc_games, 'top_ps_games': top_ps_games}

  ''' Rofi window logic loop '''
  launch_rofi(cur, games)

  con.commit()
  con.close()
