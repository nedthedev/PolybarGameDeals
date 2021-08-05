#!/usr/bin/python3 

'''
  This script is for fetching and parsing the Playstation deals, deals from psdeals.net
'''

from sqlite3.dbapi2 import converters
import requests
import time
import re
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
  _GAME_LOOKUP_URL = "https://psdeals.net/us-store/search?search_query="
  _SLEEP_DURATION = 5 # the number of seconds to sleep between page requests
  _PS_PLUS_PRICE = "99.99" # a default price for PS+ only deals (arbitrary)



  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  ''' Fetches the top deals pages, scrapes them, and gathers the relevant data '''
  @staticmethod
  def get_top_deals(pages=None, upper_price=None):
    ''' set the number of pages to fetch '''
    if(pages == None): pages = PS._TOP_DEALS_PAGES
    
    parsed_data = []
    for _page in range(pages):
      tmp = PS.get_and_parse(f"{PS._TOP_DEALS_URL}{_page+1}", PS._parse_top_deals)
      if(tmp): parsed_data.append(tmp)
      else: return None

    ''' Join the pages of games into one list '''
    joined_list = []
    for list_ in parsed_data:
      joined_list += list_
    return joined_list

  ''' A utility method to return the class variable _PS_PLUS_PRICE '''
  @staticmethod
  def ps_plus_price():
    return float(PS._PS_PLUS_PRICE)

  @staticmethod
  def get_your_deals(urls=None):
    data = []
    for url in urls:
      game = PS.get_and_parse(url, PS._parse_your_deals)
      print(game)
      data.append(game)

  @staticmethod
  def is_valid(url):
    return re.search(fr"^{PS._PS_DEALS_URL}/..-store/game/\d+.*", url)

  @staticmethod
  def get_gid(url):
    return url.split("game/")[1].split("/")[0]

  @staticmethod
  def get_and_parse(url, parser):
    ''' Make the request to download the pages '''
    data = PS._make_request(url)
    
    ''' if data was retrieved then parse it, otherwise return none '''
    if(data): return parser(data.text, url)
    else: return None



  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  ''' Makes a request for the provided url '''
  @staticmethod
  def _make_request(url):
    r = requests.get(url)
    if(r.status_code == 200):
      time.sleep(PS._SLEEP_DURATION)
      return r
    return None

  ''' The deal page scraper and data parser '''
  @staticmethod
  def _parse_top_deals(data, _):
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
          must handle whether or not it's days, hours, or doesn't exist 
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
      if(ps_deals_url): 
        ps_deals_url = ps_deals_url.text
        psdeals_gid = PS.get_gid(ps_deals_url)

      cover_image = game.find("source")
      if(cover_image):
        cover_image = cover_image["data-srcset"].split(", ")[1].split(" ")[0]
        pss_gid = cover_image.split("/99/")[1].split("/0/")[0]
      else:
        cover_image = None
        pss_gid = None

      parsed_data.append({"title": title, "full_price": full_price, "sale_price": sale_price, "cover_image": cover_image, "gid": psdeals_gid, "days_remaining": days_remaining, "url": f"{PS._PS_DEALS_URL}{ps_deals_url}", "pss_url": f"{PS._PS_STORE_URL}{pss_gid}", "title_length": f"{len(title)}"})
    return parsed_data

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
    if(cover_image):
      cover_image = cover_image["data-srcset"].split(", ")[1].split(" ")[0]

    gid = PS.get_gid(url)

    return {"title": title, "full_price": full_price, "sale_price": sale_price, "cover_image": cover_image, "gid": gid, "url": url, "title_length": len(title)}
