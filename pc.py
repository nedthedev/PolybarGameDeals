#!/usr/bin/python3 

import requests

class PC:
  #####################
  '''   VARIABLES   '''
  #####################
  _UPPER_PRICE = 10
  _YOUR_DEALS_URL = "https://www.cheapshark.com/api/1.0/games?ids="
  _TOP_DEALS_URL = "https://www.cheapshark.com/api/1.0/deals?upperPrice="
  _DEAL_URL = "https://www.cheapshark.com/redirect?dealID="



  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  @classmethod
  def get_top_deals(cls, upper_price=None):
    if(upper_price == None): upper_price = cls._UPPER_PRICE
    
    ''' Fetch the deals '''
    data = cls.__make_request(f"{cls._TOP_DEALS_URL}{upper_price}")
    if(data):
      data = cls.__parse_data(data)
      return data
    return None

  @classmethod
  def get_your_deals(cls):
    print("Fetching your deals...")



  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  @staticmethod
  def __make_request(url):
    r = requests.get(url)
    if(r.status_code == 200):
      return r.json()
    return None

  ''' Parse the deals '''
  @classmethod
  def __parse_data(cls, data):
    parsed_data = []
    for game in data:
      parsed_data.append({"title": game["title"], "full_price": game["normalPrice"], "sale_price": game["salePrice"], "cover_image": game["thumb"], "url": f"{cls._DEAL_URL}{game['dealID']}"})
    return parsed_data
