#!/usr/bin/python3

'''
  This is a collection of functions shared between the different platforms
'''

import requests

from ..utils.db_enums import DB_Columns


def create_game_dictionary(title,
                           full_price,
                           sale_price,
                           cover_image,
                           gid,
                           url):
    return {
        DB_Columns.TITLE.value: title,
        DB_Columns.FULL_PRICE.value: full_price,
        DB_Columns.SALE_PRICE.value: sale_price,
        DB_Columns.COVER_IMAGE.value: cover_image,
        DB_Columns.GID.value: gid,
        DB_Columns.URL.value: url,
        DB_Columns.TITLE_LENGTH.value: len(title)
    }


''' A shared function that just makes and returns the request, any extra
    behavior will be done by the class calling the function '''


def make_request_(url):
    try:
        r = requests.get(url)
        if(r.status_code == 200):
            return r
        else:
            return None
    except Exception:
        return None
