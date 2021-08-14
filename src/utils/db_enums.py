#!/usr/bin/python3

from enum import Enum


class DB_Tables(Enum):
    TOP_PC = "TOP_PC"
    PC_WISHLIST = "PC_WISHLIST"
    TOP_PS = "TOP_PS"
    PS_WISHLIST = "PS_WISHLIST"


class DB_Indices(Enum):
    TITLE = 0
    FULL_PRICE = 1
    SALE_PRICE = 2
    COVER_IMAGE = 3
    URL = 4
    GID = 5
    UPDATE_TIME = 6
    TITLE_LENGTH = 7


class DB_Columns(Enum):
    TITLE = "title"
    FULL_PRICE = "full_price"
    SALE_PRICE = "sale_price"
    COVER_IMAGE = "cover_image"
    UPDATE_TIME = "update_time"
    GID = "gid"
    URL = "url"
    TITLE_LENGTH = "title_length"
