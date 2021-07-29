#!/usr/bin/python3

'''
  This is a collection of all the rofi related functions
'''

from enum import Enum
import subprocess

from .db_calls import DB_Calls, Tables, DB_Indices
from ..platforms.ps import PS



''' Selection enum for picking what platform of games to browse '''
class Categories(Enum):
  TOP_PC = "Top PC Deals\n"
  TOP_PS = "Top Playstation Deals\n"

''' The main rofi logic loop wrapped in a function '''
def launch_rofi(cur, games, title_lengths, browser):
  while(True):
    category = choose_category()
    if(category):
      while(True):
        chosen_game, _table = choose_game(category, games, title_lengths)
        if(chosen_game):
          url = DB_Calls.get_game_url(cur, _table, chosen_game)
          if(url): open_url(url, browser)
          else: break
        else: break
    else: break

''' Rofi window to select what platform of games to browse '''
def choose_category():
  options = ""
  rows = 0
  for val in Categories:
    options += val.value
    rows+=1
  category = subprocess.run(["rofi", "-dmenu", "-p", "Choose category", "-lines", f"{rows}", "-columns", "1"], input=str.encode(f"{options}", encoding="UTF-8"), stdout=subprocess.PIPE)
  if(category.returncode > 0): return None
  else: return category.stdout.decode("UTF-8")

''' Check the category that was chosen '''
def check_category(category):
  print(category)

''' Rofi window to select the game you want to see more about '''
def choose_game(category, games, title_lengths):
  _GO_UP = "...Choose Category\n"
  _GAME_LENGTH_ADDON = 3
  rofi_string = _GO_UP
  longest_title = 0
  if(category == Categories.TOP_PC.value):
    _table = Tables.TOP_PC.value
    longest_title = title_lengths['longest_pc_title']
    for game in games['top_pc_games']:
      rofi_string+=(f"{stretch_string(game[DB_Indices.TITLE.value], longest_title)} ${game[DB_Indices.SALE_PRICE.value]:.2f}\n")
  elif(category == Categories.TOP_PS.value):
    _table = Tables.TOP_PS.value
    longest_title = title_lengths['longest_ps_title']
    for game in games['top_ps_games']:
      if(game[DB_Indices.SALE_PRICE.value] == PS.ps_plus_price()): rofi_string+=(f"{stretch_string(game[DB_Indices.TITLE.value], longest_title)} $PS+")
      else: rofi_string+=(f"{stretch_string(game[DB_Indices.TITLE.value], longest_title)} ${game[DB_Indices.SALE_PRICE.value]:.2f}")
      rofi_string+="\n"
  else: return None, None
  chosen_game = subprocess.run(["rofi", "-dmenu", "-p", "Search game", "-lines", "12", "-columns", "2", "-width", f"{(longest_title+_GAME_LENGTH_ADDON)}"], stdout=subprocess.PIPE, input=str.encode(rofi_string, encoding="UTF-8"))
  if(chosen_game.returncode == 0): chosen_game = chosen_game.stdout.decode("UTF-8").split("$")[0].rstrip()
  else: chosen_game = None
  return chosen_game, _table

''' Rofi window confirming whether or not you want to open the link '''
def open_url(url, browser):
  yes = "Yes\n"
  no = "No\n"
  choice = subprocess.run(["rofi", "-dmenu", "-p", f"Open: {url}", "-lines", "2", "-columns", "1"], input=str.encode(f"{yes}{no}", encoding="UTF-8"), stdout=subprocess.PIPE).stdout.decode("UTF-8")
  if(choice == yes): subprocess.run([browser, url])

def stretch_string(string, length=None):
  if(len(string) >= length):
    difference = len(string) - length
    string = string[:-difference-3] + "..."
  else:
    for _ in range(length-len(string)):
      string += " "
  return string