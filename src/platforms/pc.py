#!/usr/bin/python3

'''
  This script is for fetching and parsing the PC deals. All deals are
  discovered using the cheapshark.com API
'''

import re
from enum import Enum

from src.utils.db_calls import DB_Calls
from src.utils.db_enums import DB_Columns, DB_Tables
from src.platforms.shared import create_game_dictionary, make_request_


class Top_Deals_Indices(Enum):
    TITLE = "title"
    NORMAL_PRICE = "normalPrice"
    SALE_PRICE = "salePrice"
    COVER_IMAGE = "thumb"
    DEAL_ID = "dealID"
    GAME_ID = "gameID"


class Your_Deals_Indices(Enum):
    INFO = "info"
    DEALS = "deals"
    TITLE = "title"
    NORMAL_PRICE = "retailPrice"
    SALE_PRICE = "price"
    COVER_IMAGE = "thumb"
    DEAL_ID = "dealID"


class PC:
    _BASE_URL = "https://www.cheapshark.com"
    _YOUR_DEALS_URL = f"{_BASE_URL}/api/1.0/games?ids="
    _TOP_DEALS_URL = f"{_BASE_URL}/api/1.0/deals?upperPrice="
    _DEAL_URL = f"{_BASE_URL}/redirect?dealID="
    _GAME_LOOKUP_URL = f"{_BASE_URL}/api/1.0/games?title="

    @staticmethod
    def get_top_deals(upper_price):
        """Makes a request to get the top deals, parses them, and returns that
           data. If an upper_price is provided no deals greater than that
           amount will be discovered.

        :param upper_price: the upper price limit for pc deals
        :type upper_price:  float or int
        :return:            parsed data for adding to database, or None
        :rtype:             list or None
        """
        data = PC._make_request(f"{PC._TOP_DEALS_URL}{upper_price}")
        if(data):
            return PC._parse_data(data)
        return None

    @staticmethod
    def get_wishlist_deals(cur, ids):
        """Make request for the given id string.

        :param cur: the database cursor object
        :type cur:  cursor
        :param ids: a formatted string of ids for request
        :type ids:  str
        :return:    parsed data for adding to database if all goes well,
                    or None
        :rtype:     list or None
        """
        id_string = ""
        update_ids = []
        for index, id_ in enumerate(ids):
            if(PC.is_valid(id_)):
                # Form the valid string of ids for fetching data from api
                # with one request
                if(not index == len(ids)-1):
                    id_string += f"{id_},"
                else:
                    id_string += f"{id_}"
                # If it is in the database then we will update
                if(DB_Calls.game_exists(
                   cur, DB_Tables.PC_WISHLIST.value, id_)):
                    update_ids.append(id_)
        data = PC._make_request(f"{PC._YOUR_DEALS_URL}{id_string}")
        if(data):
            return update_ids, PC._parse_wishlist_deals(data)
        return None, None

    @staticmethod
    def is_valid(id_):
        """Check the the url matches the proper url regex.

        :param id_: id to test
        :type id_:  int
        :return:    True if valid, False if invalid
        :rtype:     bool
        """
        return re.search(r"^\d+$", str(id_))

    @staticmethod
    def search_url(game_name):
        """Return the url to search for game.

        :param game_name: the title of the game you want to lookup
        :type game_name:  str
        :return:          the url for searching the game
        :rtype:           str
        """
        return f"{PC._GAME_LOOKUP_URL}{game_name}"

    @staticmethod
    def _make_request(url):
        """Makes a request for the provided url.

        :param url: url to make request for
        :type url:  str
        :return:    jsonified request data on successful request, or None
        :rtype:     dict or None
        """
        r = make_request_(url)
        if(r):
            return r.json()
        return None

    @staticmethod
    def _parse_data(data):
        """Parse the provided data for the information we need.

        :param data: api data to parse
        :type data:  dict
        :return:     a list of dictionaries representing each game
        :rtype:      list
        """
        parsed_data = []
        titles = []
        for game in data:
            title = game[Top_Deals_Indices.TITLE.value]
            full_price = float(game[Top_Deals_Indices.NORMAL_PRICE.value])
            sale_price = float(game[Top_Deals_Indices.SALE_PRICE.value])
            cover_image = game[Top_Deals_Indices.COVER_IMAGE.value]
            url = f"{PC._DEAL_URL}{game[Top_Deals_Indices.DEAL_ID.value]}"
            gid = game[Top_Deals_Indices.GAME_ID.value]

            # Unfortunately, or fortunately?, the api can have lots of
            # duplicates, some with different prices, so I must do some
            # checking to remove dupes.
            if(title not in titles):  # Add title if it hasn't been added
                titles.append(title)
                parsed_data.append(create_game_dictionary(
                    title, full_price, sale_price, cover_image, gid, url))
            else:  # if title is already addded, check if it's cheaper
                for existing_game in parsed_data:
                    if((title ==
                        existing_game[Top_Deals_Indices.TITLE.value]) and
                        (sale_price <
                            existing_game[DB_Columns.SALE_PRICE.value])):
                        existing_game.update({
                            DB_Columns.SALE_PRICE.value: sale_price,
                            DB_Columns.URL.value: url})
        return parsed_data

    @staticmethod
    def _parse_wishlist_deals(data):
        """Parse the provided data for the information we need.

        :param data: api data to parse
        :type data:  dict
        :return:     a list of dictionaries representing each game
        :rtype:      list
        """
        games = []
        for game in data:
            gid = int(game)

            game = data[game]

            info = game[Your_Deals_Indices.INFO.value]
            title = info[Your_Deals_Indices.TITLE.value]
            cover_image = info[Your_Deals_Indices.COVER_IMAGE.value]

            deal = game[Your_Deals_Indices.DEALS.value][0]
            full_price = float(deal[Your_Deals_Indices.NORMAL_PRICE.value])
            sale_price = float(deal[Your_Deals_Indices.SALE_PRICE.value])
            url = f"{PC._DEAL_URL}{deal[Your_Deals_Indices.DEAL_ID.value]}"

            games.append(create_game_dictionary(
                title, full_price, sale_price, cover_image, gid, url))
        return games
