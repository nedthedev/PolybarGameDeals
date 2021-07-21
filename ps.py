#!/usr/bin/python3 

'''
  
'''

import requests
import time
from bs4 import BeautifulSoup

class PS:
  #####################
  '''   VARIABLES   '''
  #####################
  _TOP_DEALS_PAGES = 2
  _TOP_DEALS_URL = "https://psdeals.net/us-store/collection/top_rated_sale?platforms=ps4&page="
  _YOUR_DEALS_URL = "https://psdeals.net/us-store/game/"
  _PS_DEALS_URL = "https://psdeals.net"
  _PS_STORE_URL = "https://store.playstation.com/en-us/product/"
  _SLEEP_DURATION = 5



  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  @classmethod
  def get_top_deals(cls, pages=None):
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
    
    ''' update the database '''
    cls._update_db(parsed_data)

    ''' Join the pages of games into one list '''
    joined_list = []
    for list_ in parsed_data:
      joined_list = joined_list + list_
    return joined_list

  @classmethod
  def get_your_deals(cls):
    # Search for alt="Game cover"...
    # Search for class="old_price" to determine if on sale
    # Search for class="font-weight-bold h4 underline-span" for current price
    return

  

  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  @staticmethod
  def __make_request(url):
    r = requests.get(url)
    if(r.status_code == 200):
      return r
    return None

  @classmethod
  def __parse_top_deals(cls, data):
    html = BeautifulSoup(data, "html.parser")
    games = html.find_all("div", {"class": ["game-collection-item-col"]})
    parsed_data = []
    for game in games:
      title = game.find("p", "game-collection-item-details-title")
      if(title): title = title.text

      full_price = game.find("span", {"class": ["game-collection-item-regular-price"]})
      if(full_price): full_price = float(full_price.text[1:])

      sale_price = game.find("span", {"class": ["game-collection-item-discount-price"]})
      if(sale_price): sale_price = float(sale_price.text[1:])

      days_remaining = game.find("p", {"class": ["game-collection-item-end-date"]})
      if(days_remaining): 
        try:
          days_remaining = int(''.join(filter(str.isdigit, days_remaining.text))) # this error out when it says "Ends in a day"
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

      parsed_data.append({"title": title, "full_price": full_price, "sale_price": sale_price, "cover_image": cover_image, "days_remaining": days_remaining, "url": f"{cls._PS_DEALS_URL}{ps_deals_url}", "pss_url": f"{cls._PS_STORE_URL}{gid}"})
    return parsed_data

  @staticmethod
  def _parse_your_deals(data):
    return

  @staticmethod
  def _update_db(data):
    return
