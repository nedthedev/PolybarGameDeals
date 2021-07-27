#!/usr/bin/python3 

'''
  This script is for fetching and parsing the Playstation deals, deals from psdeals.net
'''

import requests
import time
from bs4 import BeautifulSoup

class PS:
  #####################
  '''   VARIABLES   '''
  #####################
  _TOP_DEALS_PAGES = 2  # this is the number of pages that contain deals
  _TOP_DEALS_URL = "https://psdeals.net/us-store/collection/top_rated_sale?platforms=ps4&page="
  _YOUR_DEALS_URL = "https://psdeals.net/us-store/game/"
  _PS_DEALS_URL = "https://psdeals.net"
  _PS_STORE_URL = "https://store.playstation.com/en-us/product/"
  _SLEEP_DURATION = 5 # the number of seconds to sleep between page requests
  _PS_PLUS_PRICE = "99.99" # a default price for PS+ only deals (arbitrary)



  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  ''' Fetches the top deals pages, scrapes them, and gathers the relevant data '''
  @classmethod
  def get_top_deals(cls, pages=None, upper_price=None):
    ''' set the number of pages to fetch '''
    if(pages == None): pages = cls._TOP_DEALS_PAGES
    
    parsed_data = []
    for _page in range(pages):
      ''' Make the request to download the pages '''
      data = cls.__make_request(f"{cls._TOP_DEALS_URL}{_page+1}")
      
      ''' if data was retrieved then parse it, otherwise return none '''
      if(data): parsed_data.append(cls.__parse_top_deals(data.text))
      else: return None
    
      ''' Sleep unless we just fetched the last page '''
      if(not _page+1 == pages):
        time.sleep(cls._SLEEP_DURATION)

    ''' Join the pages of games into one list '''
    joined_list = []
    for list_ in parsed_data:
      joined_list += list_
    return joined_list

  ''' A utility method to return the class variable _PS_PLUS_PRICE '''
  @classmethod
  def ps_plus_price(cls):
    return float(cls._PS_PLUS_PRICE)

  @classmethod
  def get_your_deals(cls):
    # Search for alt="Game cover"...
    # Search for class="old_price" to determine if on sale
    # Search for class="font-weight-bold h4 underline-span" for current price
    return

  

  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  ''' Makes a request for the provided url '''
  @staticmethod
  def __make_request(url):
    r = requests.get(url)
    if(r.status_code == 200):
      return r
    return None

  ''' The deal page scraper and data parser '''
  @classmethod
  def __parse_top_deals(cls, data):
    html = BeautifulSoup(data, "html.parser")
    games = html.find_all("div", {"class": ["game-collection-item-col"]})
    parsed_data = []
    for game in games:
      title = game.find("p", "game-collection-item-details-title")
      if(title): title = title.text.rstrip() # some titles have trailing space

      full_price = game.find("span", {"class": ["game-collection-item-regular-price"]})
      if(full_price): full_price = float(full_price.text[1:])

      sale_price = game.find("span", {"class": ["game-collection-item-discount-price"]})
      if(sale_price): sale_price = float(sale_price.text[1:])
      else: sale_price = cls._PS_PLUS_PRICE

      ''' There are many different indicator of time left for the deal, so I
          must handle whether or not it's days, hours, or doens't exist 
      '''
      days_remaining = game.find("p", {"class": ["game-collection-item-end-date"]})
      if(days_remaining): 
        try:
          if("hours" in days_remaining.text): days_remaining = "< 1"
          else: days_remaining = int(''.join(filter(str.isdigit, days_remaining.text)))
        except Exception:
          days_remaining = 1
      else: days_remaining = -1

      ps_deals_url = game.find("span", {"itemprop": ["url"]})
      if(ps_deals_url): ps_deals_url = ps_deals_url.text

      cover_image = game.find("source")
      if(cover_image):
        cover_image = cover_image["data-srcset"].split(", ")[1].split(" ")[0]
        gid = cover_image.split("/99/")[1].split("/0/")[0]
      else:
        cover_image = None
        gid = None

      parsed_data.append({"title": title, "full_price": full_price, "sale_price": sale_price, "cover_image": cover_image, "days_remaining": days_remaining, "url": f"{cls._PS_DEALS_URL}{ps_deals_url}", "pss_url": f"{cls._PS_STORE_URL}{gid}", "title_length": f"{len(title)}"})
    return parsed_data

  @staticmethod
  def _parse_your_deals(data):
    return
