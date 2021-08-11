#!/usr/bin/python3 

'''
  This script is for fetching and parsing the Playstation deals, deals from psdeals.net
'''

import time
import re
from bs4 import BeautifulSoup

from .shared import create_game_dictionary, make_request_

class PS:
  #####################
  '''   VARIABLES   '''
  #####################
  _TOP_DEALS_PAGES = 2  # this is the number of pages that contain deals
  _PS_DEALS_URL = "https://psdeals.net"
  _TOP_DEALS_URL = f"{_PS_DEALS_URL}/collection/top_rated_sale?platforms=ps4&page="
  _YOUR_DEALS_URL = f"{_PS_DEALS_URL}/game/"
  _GAME_LOOKUP_URL = f"{_PS_DEALS_URL}/search?search_query="
  _SLEEP_DURATION = 5 # the number of seconds to sleep between page requests
  _PS_PLUS_PRICE = "99.99" # a default price for PS+ only deals



  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  ''' Fetches the top deals pages, scrapes them, and gathers the relevant data '''
  @staticmethod
  def get_top_deals(pages=None, upper_price=None):
    ''' set the number of pages to fetch '''
    if(pages == None): pages = PS._TOP_DEALS_PAGES
    
    parsed_data = []
    for _page in range(1, pages+1):
      if(_page == PS._TOP_DEALS_PAGES): sleep = False
      else: sleep = True

      ''' Make the request to download the pages '''
      data = PS._make_request(f"{PS._TOP_DEALS_URL}{_page}", sleep)
      
      ''' if data was retrieved then parse it, otherwise return none.
          This is questionable, but I think it best to update all the data 
          at the same time... '''
      if(data): parsed_data.append(PS._parse_top_deals(data.text))
      else: return None

    ''' Join the pages of games into one list '''
    joined_list = []
    for list_ in parsed_data: joined_list += list_
    return joined_list

  ''' Get all of your top deals '''
  @staticmethod
  def get_your_deals(url, sleep=True):
    ''' Make the request to download the pages '''
    game = PS._make_request(url, sleep)

    ''' if data was retrieved then parse it, otherwise return none '''
    if(game): return PS._parse_your_deals(game.text, url)
    else: return None

  ''' A utility method to return the class variable _PS_PLUS_PRICE '''
  @staticmethod
  def ps_plus_price():
    return float(PS._PS_PLUS_PRICE)

  ''' Check the the url matches the proper url regex '''
  @staticmethod
  def is_valid(url):
    return re.search(fr"^{PS._PS_DEALS_URL}/..-store/game/\d+/.*", url)

  ''' Split the gid out of the url '''
  @staticmethod
  def get_gid(url):
    try: return url.split("game/")[1].split("/")[0]
    except Exception: return ""

  ''' Return the url to search for game '''
  @staticmethod
  def search_url(game_name):
    return f"{PS._GAME_LOOKUP_URL}{game_name}"



  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  ''' Makes a request for the provided url '''
  @staticmethod
  def _make_request(url, sleep=True):
    r = make_request_(url)
    if(r and sleep): time.sleep(PS._SLEEP_DURATION)
    return r

  ''' The deal page scraper and data parser '''
  @staticmethod
  def _parse_top_deals(data):
    html = BeautifulSoup(data, "html.parser")
    games = html.find_all("div", {"class": ["game-collection-item-col"]})
    parsed_data = []
    for game in games:
      title = game.find("p", "game-collection-item-details-title")
      if(title): title = title.text.rstrip() # some titles have trailing space

      full_price = game.find("span", {"class": ["game-collection-item-regular-price"]})
      if(full_price): full_price = float(full_price.text[1:])

      sale_price = game.find("span", {"class": ["game-collection-item-discount-price"]})
      if(sale_price): 
        ''' Try to convert to float, if it fails then the game is "FREE"! '''
        try: sale_price = float(sale_price.text[1:])
        except: sale_price = 0.00
      else: sale_price = PS._PS_PLUS_PRICE

      ''' There are many different indicators of time left for the deal, so I
          must handle whether or not it's days, hours, or doesn't exist '''
      days_remaining = game.find("p", {"class": ["game-collection-item-end-date"]})
      if(days_remaining): 
        try:
          if("hours" in days_remaining.text): days_remaining = "< 1"
          else: days_remaining = int(''.join(filter(str.isdigit, days_remaining.text)))
        except Exception: days_remaining = 1
      else: days_remaining = -1

      ps_deals_url = game.find("span", {"itemprop": ["url"]})
      if(ps_deals_url): 
        ps_deals_url = f"{PS._PS_DEALS_URL}{ps_deals_url.text}"
        psdeals_gid = PS.get_gid(ps_deals_url)

      cover_image = game.find("source")
      if(cover_image): cover_image = cover_image["data-srcset"].split(", ")[1].split(" ")[0]
      else: cover_image = None

      parsed_data.append(create_game_dictionary(title, full_price, sale_price, cover_image, psdeals_gid, ps_deals_url))
    return parsed_data

  ''' Individual game pages have different html than top pages, so we must scrape these
      differently '''
  @staticmethod
  def _parse_your_deals(data, url):
    html = BeautifulSoup(data, "html.parser")
    title = html.find("div", {"class": ["game-title-info-name"]})
    if(title): title = title.text.rstrip() # some titles have trailing space

    full_price = html.find("span", {"class": ["game-collection-item-regular-price"]})
    if(full_price): full_price = float(full_price.text[1:])

    sale_price = html.find("span", {"class": ["game-collection-item-discount-price"]})
    if(sale_price): sale_price = float(sale_price.text[1:])
    else: sale_price = full_price

    cover_image = html.find("source")
    if(cover_image): cover_image = cover_image["data-srcset"].split(", ")[1].split(" ")[0]

    gid = PS.get_gid(url)

    return create_game_dictionary(title, full_price, sale_price, cover_image, gid, url)
