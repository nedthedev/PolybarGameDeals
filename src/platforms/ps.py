#!/usr/bin/python3

'''
  This script is for fetching and parsing the Playstation deals, deals from
  psdeals.net
'''

import time
import re
from bs4 import BeautifulSoup

from src.utils.db_enums import DB_Tables
from src.utils.db_calls import DB_Calls
from src.platforms.shared import create_game_dictionary, make_request_


class PS:
    _PS_DEALS_URL = "https://psdeals.net"
    _TOP_DEALS_URL = (f"{_PS_DEALS_URL}/collection/" +
                      "top_rated_sale?platforms=ps4&page=")
    _YOUR_DEALS_URL = f"{_PS_DEALS_URL}/game/"
    _GAME_LOOKUP_URL = f"{_PS_DEALS_URL}/search?search_query="
    _TOP_DEALS_PAGES = 2  # this is the number of pages that contain deals
    _SLEEP_DURATION = 5  # the number of seconds to sleep between page requests
    _PS_PLUS_PRICE = "99.99"  # a default price for PS+ only deals

    @staticmethod
    def get_top_deals(_):
        """Fetches and scrapes the top deals.

        :param _: useless
        :type _:  *
        :return:  a list of dictionaries representing games
        :rtype:   list
        """
        parsed_data = []
        for _page in range(1, PS._TOP_DEALS_PAGES+1):
            if(_page == PS._TOP_DEALS_PAGES):
                sleep = False
            else:
                sleep = True

            # Make the request to download the pages
            data = PS._make_request(f"{PS._TOP_DEALS_URL}{_page}", sleep)

            # if data was retrieved then parse it, otherwise return none.
            # This is questionable, but I think it best to update all the data
            # at the same time...
            if(data):
                parsed_data.append(PS._parse_top_deals(data.text))
            else:
                return None

        # Join the pages of games into one list
        joined_list = []
        for list_ in parsed_data:
            joined_list += list_
        return joined_list

    @staticmethod
    def get_wishlist_deals(cur, urls):
        """Fetches and scrapes wishlist deals.

        :param cur:  database cursor
        :type cur:   Cursor
        :param urls: a list of wishlist games' urls
        :type urls:  list
        :return:     list of games to update and list of games to add
        :rtype:      list, list or None, None
        """
        new_games = []
        games_to_update = []
        for index, url in enumerate(urls):
            if(PS.is_valid(url)):
                gid = PS.get_gid(url)
                # If the game already exists in the database then we need
                # only update
                if(DB_Calls.game_exists(
                   cur, DB_Tables.PS_WISHLIST.value, gid)):
                    games_to_update.append(gid)
                # We must fetch the data for every game, because every game
                # provided needs updating
                if(index == len(urls)-1):
                    sleep = False
                else:
                    sleep = True
                game = PS.get_your_deals(url, sleep)
                if(game):
                    new_games.append(game)
        if(new_games):
            return games_to_update, new_games
        return None, None

    @staticmethod
    def get_your_deals(url, sleep=True):
        """Fetch and parse game at the url.

        :param url:   the url of the game to parse
        :type url:    str
        :param sleep: whether or not to sleep after request, defaults to True
        :type sleep:  bool, optional
        :return:      dictionary representing game from the url
        :rtype:       dict
        """
        # Make the request to download the pages
        game = PS._make_request(url, sleep)

        # if data was retrieved then parse it, otherwise return none
        if(game):
            return PS._parse_your_deals(game.text, url)
        else:
            return None

    @staticmethod
    def ps_plus_price():
        """Just a getter for the _PS_PLUS_PRICE variable

        :return: class variable _PS_PLUS_PRICE
        :rtype:  str
        """
        return float(PS._PS_PLUS_PRICE)

    @staticmethod
    def is_valid(url):
        """Check the url matches the proper url regex.

        :param url: the url to check validity of
        :type url:  str
        :return:    boolean whether or not it's a valid url
        :rtype:     bool
        """
        return re.search(fr"^{PS._PS_DEALS_URL}/..-store/game/\d+/.*", url)

    @staticmethod
    def get_gid(url):
        """Split game id out of the url.

        :param url: the url to get game id out of
        :type url:  str
        :return:    the game id, if invalid then None
        :rtype:     str or None
        """
        try:
            return url.split("game/")[1].split("/")[0]
        except Exception:
            return None

    @staticmethod
    def search_url(game_name):
        """Return the url to search for the game_name.

        :param game_name: the name of the game to search
        :type game_name:  str
        :return:          the url to use to search for the game
        :rtype:           str
        """
        return f"{PS._GAME_LOOKUP_URL}{game_name}"

    @staticmethod
    def _make_request(url, sleep=True):
        """Makes a request for the provided url.

        :param url:   the url to make a request for
        :type url:    str
        :param sleep: whether or not to sleep after request, defaults to True
        :type sleep:  bool, optional
        :return:      request result
        :rtype:       request
        """
        r = make_request_(url)
        if(r and sleep):
            time.sleep(PS._SLEEP_DURATION)
        return r

    @staticmethod
    def _parse_top_deals(data):
        """The deal page scraper and data parser.

        :param data: the data from the web page to scrape
        :type data:  request.text
        :return:     a list of dictionaries representing games
        :rtype:      list
        """
        html = BeautifulSoup(data, "html.parser")
        games = html.find_all("div", "game-collection-item-col")
        parsed_data = []
        for game in games:
            title = game.find("p", "game-collection-item-details-title")
            if(title):
                title = title.text.rstrip()  # some titles have trailing space

            full_price = game.find(
                "span", {"class": ["game-collection-item-regular-price"]})
            if(full_price):
                full_price = float(full_price.text[1:])

            sale_price = game.find(
                "span", {"class": ["game-collection-item-discount-price"]})
            if(sale_price):
                # Try to convert to float, if it fails then the game is free
                try:
                    sale_price = float(sale_price.text[1:])
                except Exception:
                    sale_price = 0.00
            else:
                sale_price = PS._PS_PLUS_PRICE

            # There are many different indicators of time left for the deal, so
            # I must handle whether or not it's days, hours, or doesn't exist
            days_remaining = game.find(
                "p", {"class": ["game-collection-item-end-date"]})
            if(days_remaining):
                try:
                    if("hours" in days_remaining.text):
                        days_remaining = "< 1"
                    else:
                        days_remaining = int(
                            ''.join(filter(str.isdigit, days_remaining.text)))
                except Exception:
                    days_remaining = 1
            else:
                days_remaining = -1

            ps_deals_url = game.find("span", {"itemprop": ["url"]})
            if(ps_deals_url):
                ps_deals_url = f"{PS._PS_DEALS_URL}{ps_deals_url.text}"
                psdeals_gid = PS.get_gid(ps_deals_url)

            cover_image = game.find("source")
            if(cover_image):
                cover_image = cover_image["data-srcset"].split(", ")[
                    1].split(" ")[0]
            else:
                cover_image = None

            parsed_data.append(create_game_dictionary(
                                  title,
                                  full_price,
                                  sale_price,
                                  cover_image,
                                  psdeals_gid,
                                  ps_deals_url))
        return parsed_data

    @staticmethod
    def _parse_your_deals(data, url):
        """Scrape the wishlist game data from the page.

        :param data: the data to be parsed
        :type data:  request.text
        :param url:  the url that the data is from
        :type url:   str
        :return:     a dictionary representing the game
        :rtype:      dict
        """
        html = BeautifulSoup(data, "html.parser")
        title = html.find("div", {"class": ["game-title-info-name"]})
        if(title):
            title = title.text.rstrip()  # some titles have trailing space

        full_price = html.find(
            "span", {"class": ["game-collection-item-regular-price"]})
        if(full_price):
            full_price = float(full_price.text[1:])

        sale_price = html.find(
            "span", {"class": ["game-collection-item-discount-price"]})
        if(sale_price):
            sale_price = float(sale_price.text[1:])
        else:
            sale_price = full_price

        cover_image = html.find("source")
        if(cover_image):
            cover_image = cover_image["data-srcset"].split(", ")[
                1].split(" ")[0]

        gid = PS.get_gid(url)
        # Reaffirm the legitamacy of the url
        if(not gid):
            return None

        return create_game_dictionary(
            title,
            full_price,
            sale_price,
            cover_image,
            gid,
            url)
