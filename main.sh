#!/usr/bin/sh

# ABOUT
# This program finds and stores all of the best deals for PC and Playstation 4 
# games from around the web. Put simply, this script calls a python script which
# prints a whole bunch of newline delimited games for rendering inside of rofi,
# and while it does that it also stores the data inside of games.db.
# 
# DATA SOURCES
# Big thanks to cheapshark.com for the PC games and their nifty api.
# Another big thanks to  psdeals.net for the playstation deals
# All PC game links are affiliate links, as per cheapshark's terms. Playstation
# links go to the psdeals.net website.
# I was initially going to use data from psprices.com, but even though their 
# robots.txt file has no rules stopping bots from scraping the pages I wanted,
# their backend does block python bots' default headers, so I chose to respect 
# their apparent wishes to block scraper and to not spoof my bot's headers.
# 
# WHY I MADE THIS
# I made this program for building a module for my polybar. When I click the
# module a rofi window will popup with the deals. My internet is not so good, so
# having a script that shows me the best deals and prevents me from needing to
# spend the time loading pages of game deals sounded pretty nice.
#
# USAGE
# The only arguments for this script are arguments that will be passed to
# main.py, so you can either run this script with the arguments or the main.py
# file with the arguments. 
# For the most part, the script is as is and doesn't really have much to tweak,
# but obviously not everybody has rofi or wants to use rofi, so feel free to
# alter this script to do whatever you want to do with the output of main.py.
# The output of main.py is in the form of json, so you can use jq and do pretty
# much anything you want to with it.

# -width -length
chosen_game=$(exec ./main.py | rofi -dmenu -p "Search game" -lines 12 -columns 2 | awk -F "$" '{print $1}' | awk '{$1=$1};1')
echo "$chosen_game"