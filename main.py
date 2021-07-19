#!/usr/bin/python3

# ABOUT
# This program finds and stores all of the best deals for PC and Playstation 4 
# games from around the web. 
# 
# DATA SOURCES
# It makes use of data from cheapshark.com and
# psdeals.net, so big thanks to them for their services. All links provided by
# this program are affiliate links for cheapshark and psdeals, so nobody is
# getting skipped over. I was initially going to use data from psprices.com, but
# even though their robots.txt file has no rules stopping bots from scraping
# the pages I wanted, their backend does block python bots by default, so I 
# chose to respect their wishes and to not spoof my bot's headers.
# 
# USAGE
# I made this program for building a module for my polybar. When I click the module # a rofi window will popup with the deals. My internet is not so good, so having 
# a script that shows me the best deals and prevents me from needing to spend 
# the time loading pages of game deals sounded pretty nice.

import sqlite3
import argparse

from pc import PC
from ps import PS

''' Scan for arguments to manage the "wishlist" games '''
def check_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-ps", help="id of game from ", action="extend", nargs="+")
  parser.add_argument("-pc", help="id of pc game from cheapshark.com, will delete from db if it already exists", action="extend", nargs="+")
  return parser.parse_args()


if __name__ == "__main__":
  ''' Create a cursor and connection for the database interactions '''
  # con = sqlite3.connect('games.db')
  # cur = con.cursor()

  ''' Modify database with any arguments '''
  args = check_args()
  # add / remove games

  ''' Get the deals '''
  pc_games = PC.get_top_deals()
  # ps_games = PS.get_top_deals()

  print("\nPC GAMES")
  for game in pc_games:
    print(f"{game['title']}\n")

  ''' Update the database '''
  # commit the new data to the database

  ''' Gather the data from the database '''
  # fetch the relevant data for rendering

  ''' Format the data to pretty printed for the rofi popup '''
  # print out the data to the bash script

  # con.commit()
  # con.close()

  exit()
