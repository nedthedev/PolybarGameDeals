#!/usr/bin/python3

'''
  This is a collection of all the rofi related functions
'''

from enum import Enum
import subprocess

from .db_calls import DB_Calls
from .db_enums import DB_Tables, DB_Indices
from ..platforms.ps import PS



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
  DELETE_GAME = "Delete Game\n"

''' The main rofi logic loop wrapped in a function '''
def launch_rofi(cur, games, title_lengths, browser):
  while(True):
    category = choose_option(Categories)
    if(category):
      if(not category == Categories.MANAGE_WISHLIST.value):
        while(True):
          chosen_game, table = choose_game(category, games, title_lengths)
          if(chosen_game):
            url = DB_Calls.get_game_url(cur, table, chosen_game)
            if(url): 
              if(confirmed(f"Open {url}")): open_url(browser, url)
              else: break
            else: break
          else: break
      elif(category == Categories.MANAGE_WISHLIST.value):
        while(True):
          chosen_wishlist = choose_option(WishlistOptions)
          if(chosen_wishlist):
            while(True):
              wishlist_option = choose_option(WishlistGameOptions)
              if(wishlist_option):
                if(wishlist_option == WishlistGameOptions.DELETE_GAME.value):
                  while(True):
                    chosen_game, table = choose_game(chosen_wishlist, games, title_lengths)
                    if(chosen_game): games = DB_Calls.delete_game_now(cur, table, chosen_game, games)
                    else: break
                # elif(wishlist_option == WishlistGameOptions.ADD_GAME.value):
                #   while(True):
                #     url = add_game_url()
                #     if(url): 
                #       if(chosen_wishlist == WishlistOptions.PC.value):
                #         if(PC.is_valid(url)):
                #           print("Adding new game")
                #         else:
                #           print("Invalid game url")
                #       elif(chosen_wishlist == WishlistOptions.PS.value):
                #         if(PS.is_valid(url)):
                #           print("Adding new game")
                #         else:
                #           print("Invalid game url")
                #       else: break
                #     else: break 
                else: break
              else: break
          else: break
      else: break
    else: break

''' Rofi window to select what platform of games to browse '''
def choose_option(Options):
  options = ""
  rows = 0
  for val in Options:
    options += val.value
    rows+=1    
  category = subprocess.run(["rofi", "-dmenu", "-p", "", "-lines", f"{rows}", "-columns", "1"], input=str.encode(f"{options}", encoding="UTF-8"), stdout=subprocess.PIPE)
  if(category.returncode > 0): return None
  else: return category.stdout.decode("UTF-8")

''' Rofi window to select the game you want to see more about '''
def choose_game(category, games, title_lengths):
  # _GO_UP = "..\n"
  _GAME_LENGTH_ADDON = 4

  rofi_string = ""
  longest_title = 0
  if(category == Categories.TOP_PC.value):
    _table = DB_Tables.TOP_PC.value
    longest_title = title_lengths[_table]
    rofi_string = form_pc_string(rofi_string, games[_table], longest_title)
  elif(category == Categories.TOP_PS.value):
    _table = DB_Tables.TOP_PS.value
    longest_title = title_lengths[_table]
    rofi_string = form_ps_string(rofi_string, games[_table], longest_title)
  elif(category == Categories.PC_WISHLIST.value or category == WishlistOptions.PC.value):
    _table = DB_Tables.PC_WISHLIST.value
    longest_title = title_lengths[_table]
    rofi_string = form_pc_string(rofi_string, games[_table], longest_title)
  elif(category == Categories.PS_WISHLIST.value or category == WishlistOptions.PS.value):
    _table = DB_Tables.PS_WISHLIST.value
    longest_title = title_lengths[_table]
    rofi_string = form_ps_string(rofi_string, games[_table], longest_title)
  else: return None, None
  chosen_game = subprocess.run(["rofi", "-dmenu", "-p", "", "-lines", "12", "-columns", "2", "-width", f"{(longest_title+_GAME_LENGTH_ADDON)}"], stdout=subprocess.PIPE, input=str.encode(rofi_string, encoding="UTF-8"))
  if(chosen_game.returncode == 0): chosen_game = chosen_game.stdout.decode("UTF-8").split("$")[0].rstrip()
  else: chosen_game = None
  return chosen_game, _table

# def url_prompt(table, )

''' Rofi window confirming whether or not you want to open the link '''
def confirmed(prompt):
  yes = "Yes\n"
  no = "No\n"
  choice = subprocess.run(["rofi", "-dmenu", "-p", f"{prompt}", "-lines", "2", "-columns", "1"], input=str.encode(f"{yes}{no}", encoding="UTF-8"), stdout=subprocess.PIPE).stdout.decode("UTF-8")
  if(choice == yes): return True
  else: return False

''' Rofi window confirming whether or not you want to open the link '''
def add_game_url():
  choice = subprocess.run(["rofi", "-dmenu", "-p", "Enter url of game to add", "-lines", "1", "-columns", "1"], input=str.encode(f"", encoding="UTF-8"), stdout=subprocess.PIPE)
  if(choice.returncode > 0): return None
  else: return choice.stdout.decode("UTF-8")

def open_url(browser, url):
  subprocess.run([browser, url])

def form_pc_string(rofi_string, games, longest_title):
  for game in games: rofi_string+=(f"{stretch_string(game[DB_Indices.TITLE.value], longest_title)} ${game[DB_Indices.SALE_PRICE.value]:.2f}\n")
  return rofi_string

def form_ps_string(rofi_string, games, longest_title):
  for game in games:
    if(game[DB_Indices.SALE_PRICE.value] == PS.ps_plus_price()): rofi_string+=(f"{stretch_string(game[DB_Indices.TITLE.value], longest_title)} $PS+")
    else: rofi_string+=(f"{stretch_string(game[DB_Indices.TITLE.value], longest_title)} ${game[DB_Indices.SALE_PRICE.value]:.2f}")
    rofi_string+="\n"
  return rofi_string

def stretch_string(string, length=None):
  # if(len(string) >= length):
  #   difference = len(string) - length
    # string = string[:-difference-3] + "..." # don't do this, it changes the title so it won't match on lookup
  # else:
  for _ in range(length-len(string)):
    string += " "
  return string