#!/usr/bin/python3

'''
  This is a collection of all the rofi related functions
'''

from enum import Enum
import subprocess
import webbrowser

from .db_calls import DB_Calls
from .db_enums import DB_Tables, DB_Indices
from ..platforms.ps import PS
from ..platforms.pc import PC



''' Selection enum for picking what platform of games to browse '''
class Categories(Enum):
  TOP_PC = "Top PC Deals\n"
  TOP_PS = "Top Playstation Deals\n"
  PC_WISHLIST = "PC Wishlist\n"
  PS_WISHLIST = "Playstation Wishlist\n"
  MANAGE_WISHLIST = "Manage Wishlists\n"

class WishlistOptions(Enum):
  PC = Categories.PC_WISHLIST.value
  PS = Categories.PS_WISHLIST.value

class WishlistGameOptions(Enum):
  # ADD_GAME = "Add Game\n" 
  SEARCH_GAME = "Search Game\n"
  DELETE_GAME = "Delete Game\n"



############################
'''   "PUBLIC" METHODS   '''
############################
''' The main rofi logic loop wrapped in a function '''
def launch_rofi(cur, games, title_lengths):
  while(True):
    category = _choose_option(Categories)
    if(category):
      if(not category == Categories.MANAGE_WISHLIST.value):
        while(True):
          chosen_game, table = _choose_game(category, games, title_lengths)
          if(chosen_game):
            url = DB_Calls.get_game_url(cur, table, chosen_game)
            if(url): 
              if(_confirmed(f"Open {url}")): _open_url(url)
              else: break
            else: break
          else: break
      elif(category == Categories.MANAGE_WISHLIST.value):
        while(True):
          chosen_wishlist = _choose_option(WishlistOptions)
          if(chosen_wishlist):
            while(True):
              wishlist_option = _choose_option(WishlistGameOptions)
              if(wishlist_option):
                if(wishlist_option == WishlistGameOptions.DELETE_GAME.value):
                  while(True):
                    chosen_game, table = _choose_game(chosen_wishlist, games, title_lengths)
                    if(chosen_game): games = DB_Calls.delete_game_now(cur, table, chosen_game, games)
                    else: break
                elif(wishlist_option == WishlistGameOptions.SEARCH_GAME.value):
                  while(True):
                    game_name = _get_input("Enter name of game")
                    if(game_name):
                      if(chosen_wishlist == WishlistOptions.PC.value):
                        url = PC.search_url(game_name)
                        if(_confirmed(f"Open {url}")): _open_url(url)
                        else: break
                      else:
                        url = PS.search_url(game_name)
                        if(_confirmed(f"Open {url}")): _open_url(url)
                        else: break
                    else: break
                else: break
              else: break
          else: break
      else: break
    else: break



#############################
'''   "PRIVATE" METHODS   '''
#############################
''' Rofi window to select what platform of games to browse '''
def _choose_option(Options):
  options = ""
  rows = 0
  for val in Options:
    options += val.value
    rows+=1    
  category = subprocess.run(["/usr/bin/rofi", "-dmenu", "-p", "", "-lines", f"{rows}", "-columns", "1"], input=str.encode(f"{options}", encoding="UTF-8"), stdout=subprocess.PIPE, shell=False)
  if(category.returncode > 0): return None
  else: return category.stdout.decode("UTF-8")

''' Rofi window to select the game you want to see more about '''
def _choose_game(category, games, title_lengths):
  _GO_UP = ""
  _ADDON = 18

  rofi_string = _GO_UP
  longest_title = 0
  if(category == Categories.TOP_PC.value):
    _table = DB_Tables.TOP_PC.value
    longest_title = title_lengths[_table]
    rofi_string = _form_pc_string(rofi_string, games[_table], longest_title)
  elif(category == Categories.TOP_PS.value):
    _table = DB_Tables.TOP_PS.value
    longest_title = title_lengths[_table]
    rofi_string = _form_ps_string(rofi_string, games[_table], longest_title)
  elif(category == Categories.PC_WISHLIST.value or category == WishlistOptions.PC.value):
    _table = DB_Tables.PC_WISHLIST.value
    longest_title = title_lengths[_table]
    rofi_string = _form_pc_string(rofi_string, games[_table], longest_title)
  elif(category == Categories.PS_WISHLIST.value or category == WishlistOptions.PS.value):
    _table = DB_Tables.PS_WISHLIST.value
    longest_title = title_lengths[_table]
    rofi_string = _form_ps_string(rofi_string, games[_table], longest_title)
  else: return None, None
  chosen_game = subprocess.run(["/usr/bin/rofi", "-dmenu", "-p", "", "-lines", "12", "-columns", "2", "-width", f"-{longest_title*2+_ADDON}"], stdout=subprocess.PIPE, input=str.encode(rofi_string, encoding="UTF-8"), shell=False)
  if(chosen_game.returncode == 0): chosen_game = chosen_game.stdout.decode("UTF-8").split("$")[0].rstrip()
  else: chosen_game = None
  return chosen_game, _table

''' Rofi window confirming whether or not you want to open the link '''
def _get_input(prompt):
  choice = subprocess.run(["/usr/bin/rofi", "-dmenu", "-p", f"{prompt}", "-lines", "2", "-columns", "1"], stdout=subprocess.PIPE, shell=False)
  if(choice.returncode == 0): return choice.stdout.decode("UTF-8")
  else: return None

''' Rofi window confirming whether or not you want to open the link '''
def _confirmed(prompt):
  yes = "Yes\n"
  no = "No\n"
  choice = subprocess.run(["/usr/bin/rofi", "-dmenu", "-p", f"{prompt}", "-lines", "2", "-columns", "1"], input=str.encode(f"{yes}{no}", encoding="UTF-8"), stdout=subprocess.PIPE, shell=False).stdout.decode("UTF-8")
  if(choice == yes): return True
  else: return False

''' Simple function to open url '''
def _open_url(url):
  webbrowser.open_new_tab(url)

''' Format the PC game deals into nice format for rendering with rofi '''
def _form_pc_string(rofi_string, games, longest_title):
  for game in games: rofi_string+=(f"{_stretch_string(game[DB_Indices.TITLE.value], longest_title)} ${game[DB_Indices.SALE_PRICE.value]:.2f}\n")
  return rofi_string

''' Format the PS game deals into nice format for rendering with rofi '''
def _form_ps_string(rofi_string, games, longest_title):
  for game in games:
    if(game[DB_Indices.SALE_PRICE.value] == PS.ps_plus_price()): rofi_string+=(f"{_stretch_string(game[DB_Indices.TITLE.value], longest_title)} $PS+")
    else: rofi_string+=(f"{_stretch_string(game[DB_Indices.TITLE.value], longest_title)} ${game[DB_Indices.SALE_PRICE.value]:.2f}")
    rofi_string+="\n"
  return rofi_string

''' Stretch the game title so that each game takes equal space '''
def _stretch_string(string, length):
  for _ in range(length-len(string)): string += " "
  return string