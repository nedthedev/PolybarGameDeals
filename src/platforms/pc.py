#!/usr/bin/python3 

'''
  This script is for fetching and parsing the PC deals, deals from cheapshark.com
'''

import requests

class PC:
  #####################
  '''   VARIABLES   '''
  #####################
  _UPPER_PRICE = 10
  _YOUR_DEALS_URL = "https://www.cheapshark.com/api/1.0/games?ids="
  _TOP_DEALS_URL = "https://www.cheapshark.com/api/1.0/deals?upperPrice="
  _DEAL_URL = "https://www.cheapshark.com/redirect?dealID="
  _GAME_LOOKUP_URL = "https://www.cheapshark.com/api/1.0/games?title="


  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  ''' Makes a request to get the top deals, parses them, and returns that data. 
      If an upper_price is provided no deals greater than that amount will be
      discovered. 
  '''
  @staticmethod
  def get_top_deals(upper_price=None):
    if(upper_price == None): upper_price = PC._UPPER_PRICE

    data = PC.__make_request(f"{PC._TOP_DEALS_URL}{upper_price}")
    if(data):
      data = PC.__parse_data(data)
      return data
    return None

  @staticmethod
  def get_your_deals(ids):
    # data = cls.__make_request(f"{cls._YOUR_DEALS_URL}{ids}")
    # if(data):
    #   data = cls.__parse_data(data)
    #   return data
    return None



  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  ''' Makes a request for the provided url (the api) ''' 
  @staticmethod
  def __make_request(url):
    r = requests.get(url)
    if(r.status_code == 200):
      return r.json()
    return None

  ''' Parse the deals '''
  @staticmethod
  def __parse_data(data):
    parsed_data = []
    titles = []
    for game in data:
      title = game["title"]
      full_price = float(game["normalPrice"])
      sale_price = float(game["salePrice"])
      cover_image = game["thumb"]
      url = f"{PC._DEAL_URL}{game['dealID']}"

      ''' 
      Unfortunately, or fortunately?, the api can have lots of duplicates, some with different prices, so I must do some checking to remove dupes.
      '''
      if(not title in titles):  # If this title hasn't been added then add it
        titles.append(title)
        parsed_data.append({"title": title, "full_price": full_price, "sale_price": sale_price, "cover_image": cover_image, "url": url, "title_length": f"{len(title)}"})
      else:   # if this title has been added, check if this one is cheaper
        for existing_game in parsed_data:
          if((title == existing_game['title']) and (sale_price < existing_game['sale_price'])):
            existing_game.update({"sale_price": sale_price, "url": url})
    return parsed_data
