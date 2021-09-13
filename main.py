#!/usr/bin/python3

'''
    This script finds and shows you some of the current best PC and Playstation
    deals. PC deals are found using a public REST API, while all playstation
    deals are scraped from https://psdeals.net/.

    Data Sources:
        All PC Deals are provided using the cheapshark API at
        https://apidocs.cheapshark.com/. When you select a PC game it will take
        you to a redirect link as per therules of the api.

        All Playstation deals are scraped from https://psdeals.net/. When you
        select a Playstation game it will take you to the game's page on the
        psdeals.net website.
'''

import sqlite3
import os
import argparse
from datetime import timedelta

from src.platforms.pc import PC
from src.platforms.ps import PS
from src.utils.db_enums import DB_Tables
from src.utils.db_calls import DB_Calls
from src.utils.rofi import launch_rofi


def check_args():
    """Parse command line arguments.

    :return: a parser object
    :rtype:  ArgumentParser
    """
    parser = argparse.ArgumentParser()
    # ----------------------------------------------------------------------- #
    parser.add_argument(
        "-r", "--rofi", help="run rofi window exclusively, do not check for\
            updates", action="store_true")
    # ----------------------------------------------------------------------- #
    parser.add_argument(
        "-s", "--silent", help="update games if necessary, use this argument\
            if you don't want a rofi window to open", action="store_true")
    # ----------------------------------------------------------------------- #
    # parser.add_argument(
    #     "-p", "--ps-plus", help="include this option to show prices and\
    #         deals available for Playstation Plus subscribers",
    #                             action="store_true")
    # ----------------------------------------------------------------------- #
    parser.add_argument("--pc-max", help="the maximum price for PC deals\
        default=15", type=int, default=15)
    # ----------------------------------------------------------------------- #
    parser.add_argument("--ps", help="url of game from https://psdeals.net/.\
        Just search for the game you want to add, copy the url, and paste it,\
            along with all other urls", action="extend", nargs="+")
    # ----------------------------------------------------------------------- #
    parser.add_argument("--pc", help="id of pc game from\
        https://www.cheapshark.com. To find the id of your game, search for\
            it at https://www.cheapshark.com/api/1.0/games?title=game-name",
                        action="extend", nargs="+")
    # ----------------------------------------------------------------------- #
    return parser.parse_args()


def update_wishlist_games(cur, table, wishlist_args, update_delay):
    """A function to update wishlist games.

    :param cur:           database cursor object
    :type cur:            Cursor
    :param table:         name of table to work on
    :type table:          str
    :param wishlist_args: list of wishlist games to add to database
    :type wishlist_args:  list
    :param update_delay:  the amount of time that must pass before updating
    :type update_delay:   timedelta
    """

    # Figure out which games need updating
    outdated_games = DB_Calls.wishlist_needs_updating(cur, table, update_delay)
    # Fetch deals for new and existing wishlist games
    if(wishlist_args or outdated_games):
        if(table == DB_Tables.PC_WISHLIST.value):
            _table = DB_Tables.PC_WISHLIST.value
            games_to_update, new_games = (
                PC.get_wishlist_deals(cur, outdated_games+wishlist_args))
        elif(table == DB_Tables.PS_WISHLIST.value):
            _table = DB_Tables.PS_WISHLIST.value
            games_to_update, new_games = (
                PS.get_wishlist_deals(cur, outdated_games+wishlist_args))
        if(new_games):
            DB_Calls.add_games(cur, _table, new_games, games_to_update)


def update_top_games(cur, table, cls, update_delay, upper_price=None):
    """A function to update the top game deals.

    :param cur:          database cursor object
    :type cur:           Cursor
    :param table:        name of table to work on
    :type table:         str
    :param cls:          the class to get top games for
    :type cls:           the platform class to get deals for
    :param update_delay: the amount of time that needs to pass
                         before fetching new data
    :type update_delay:  timedelta
    :param upper_price:  the upper price limit for pc deals, defaults to None
    :type upper_price:   float, optional
    """
    if(DB_Calls.needs_updating(cur, table, update_delay)):
        old_top = DB_Calls.get_data(cur, table)
        new_top = cls.get_top_deals(upper_price)
        if(new_top):
            DB_Calls.add_top_deals(cur, table, old_top, new_top)


if __name__ == "__main__":
    # The amount of time that must pass before updating the database
    CUSTOM_UPDATE_DELAY = timedelta(seconds=0, minutes=0, hours=12, days=0)

    # Move to the current directory
    os.chdir(os.path.dirname(__file__))

    # Create a cursor and connection for the database interactions
    con = sqlite3.connect(f'{os.getcwd()}/games.db')
    cur = con.cursor()

    # Check for any arguments
    args = check_args()

    # Remove any arguments that are already in the database. If they need
    # updating they will be found later
    if(args.pc):
        for index, id_ in enumerate(args.pc):
            if(DB_Calls.game_exists(
               cur, DB_Tables.PC_WISHLIST.value, id_=id_)):
                del args.pc[index]
    else:
        args.pc = []
    if(args.ps):
        for index, url in enumerate(args.ps):
            if(DB_Calls.game_exists(
               cur, DB_Tables.PS_WISHLIST.value, url=url)):
                del args.ps[index]
    else:
        args.ps = []

    # If we did not pass the -r option then check for updates
    if(not args.rofi):
        # update the top games
        update_top_games(cur, DB_Tables.TOP_PC.value, PC, CUSTOM_UPDATE_DELAY,
                         args.pc_max)
        update_top_games(cur, DB_Tables.TOP_PS.value, PS, CUSTOM_UPDATE_DELAY)
        # update wishlist games
        update_wishlist_games(cur, DB_Tables.PC_WISHLIST.value, args.pc,
                              CUSTOM_UPDATE_DELAY)
        update_wishlist_games(cur, DB_Tables.PS_WISHLIST.value, args.ps,
                              CUSTOM_UPDATE_DELAY)

    # Gather all games into dictionary for convenience
    games = {
        DB_Tables.TOP_PC.value: DB_Calls.get_data(
                                    cur, DB_Tables.TOP_PC.value),
        DB_Tables.TOP_PS.value: DB_Calls.get_data(
                                    cur, DB_Tables.TOP_PS.value),
        DB_Tables.PC_WISHLIST.value: DB_Calls.get_data(
                                        cur, DB_Tables.PC_WISHLIST.value),
        DB_Tables.PS_WISHLIST.value: DB_Calls.get_data(
                                        cur, DB_Tables.PS_WISHLIST.value)
    }
    # Gather all the longest titles
    title_lengths = {
        DB_Tables.TOP_PC.value: DB_Calls.get_longest_title(
                                    cur, DB_Tables.TOP_PC.value),
        DB_Tables.TOP_PS.value: DB_Calls.get_longest_title(
                                    cur, DB_Tables.TOP_PS.value),
        DB_Tables.PC_WISHLIST.value: DB_Calls.get_longest_title(
                                        cur, DB_Tables.PC_WISHLIST.value),
        DB_Tables.PS_WISHLIST.value: DB_Calls.get_longest_title(
                                        cur, DB_Tables.PS_WISHLIST.value)
    }

    # Rofi window logic loop
    if(args.rofi or not args.silent):
        launch_rofi(cur, games, title_lengths)

    con.commit()
    con.close()
