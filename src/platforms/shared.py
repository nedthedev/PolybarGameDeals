#!/usr/bin/python3

from ..utils.db_enums import DB_Columns

def create_game_dictionary(title, full_price, sale_price, cover_image, gid, url):
  return {
    DB_Columns.TITLE.value: title, 
    DB_Columns.FULL_PRICE.value: full_price, 
    DB_Columns.SALE_PRICE.value: sale_price, 
    DB_Columns.COVER_IMAGE.value: cover_image, 
    DB_Columns.GID.value: gid,
    DB_Columns.URL.value: url, 
    DB_Columns.TITLE_LENGTH.value: len(title)
  }
