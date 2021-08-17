#!/usr/bin/python3

'''
  This is a collection of functions shared between the different platforms
'''

import requests

from ..utils.db_enums import DB_Columns


def create_game_dictionary(title, full_price, sale_price, cover_image, gid, 
                           url):
    """Creates and returns a dictionary for the game.

    :param title:       the title of the game
    :type title:        str
    :param full_price:  the full price of the game
    :type full_price:   float
    :param sale_price:  the sale price of the game
    :type sale_price:   float
    :param cover_image: the cover image url for the game
    :type cover_image:  str
    :param gid:         the game id
    :type gid:          int
    :param url:         the url for the game
    :type url:          str
    :return:            a dictionary representation of the game
    :rtype:             dict
    """
    return {
        DB_Columns.TITLE.value: title,
        DB_Columns.FULL_PRICE.value: full_price,
        DB_Columns.SALE_PRICE.value: sale_price,
        DB_Columns.COVER_IMAGE.value: cover_image,
        DB_Columns.GID.value: gid,
        DB_Columns.URL.value: url,
        DB_Columns.TITLE_LENGTH.value: len(title)
    }


def make_request_(url):
    """A shared function that just makes and returns the request, any extra
       behavior will be done by the class calling the function.

    :param url: the url to make request for
    :type url:  str
    :return:    the request if successful, otherwise None
    :rtype:     request or None
    """
    try:
        r = requests.get(url)
        if(r.status_code == 200):
            return r
        else:
            return None
    except Exception:
        return None
