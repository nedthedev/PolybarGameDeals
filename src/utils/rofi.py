#!/usr/bin/python3

'''
  This is a collection of all the rofi related functions
'''

from enum import Enum
import subprocess
import webbrowser

from src.utils.db_calls import DB_Calls
from src.utils.db_enums import DB_Tables, DB_Indices
from src.platforms.ps import PS
from src.platforms.pc import PC


class Categories(Enum):
    TOP_PC = "Top PC Deals\n"
    TOP_PS = "Top Playstation Deals\n"
    PC_WISHLIST = "PC Wishlist\n"
    PS_WISHLIST = "Playstation Wishlist\n"
    MANAGE_WISHLIST = "Manage Wishlists\n"


class WishlistOptions(Enum):
    PC = Categories.PC_WISHLIST.value
    PS = Categories.PS_WISHLIST.value


class WishlistGameOptions(Enum):
    # ADD_GAME = "Add Game\n"
    SEARCH_GAME = "Search Game\n"
    DELETE_GAME = "Delete Game\n"


def launch_rofi(cur, games, title_lengths):
    """The main rofi logic loop wrapped in a function.

    :param cur:           database cursor
    :type cur:            Cursor
    :param games:         a dictionary with a list for each game platform,
                          each list containing tuples representing each game
    :type games: dict
    :param title_lengths: a dictionary with a value for each game platform
                          representing the longest game title
    :type title_lengths:  dict
    """
    while(True):
        category = _choose_option(Categories)
        if(category):
            if(not category == Categories.MANAGE_WISHLIST.value):
                while(True):
                    chosen_game, table = _choose_game(
                        category, games, title_lengths)
                    if(chosen_game):
                        url = DB_Calls.get_game_url(cur, table, chosen_game)
                        if(url):
                            if(_confirmed(f"Open {url}")):
                                _open_url(url)
                    else:
                        break
            elif(category == Categories.MANAGE_WISHLIST.value):
                while(True):
                    chosen_wishlist = _choose_option(WishlistOptions)
                    if(chosen_wishlist):
                        while(True):
                            wishlist_option = _choose_option(
                                WishlistGameOptions)
                            if(wishlist_option):
                                if(wishlist_option ==
                                   WishlistGameOptions.DELETE_GAME.value):
                                    while(True):
                                        chosen_game, table = _choose_game(
                                            chosen_wishlist,
                                            games,
                                            title_lengths)
                                        if(chosen_game):
                                            if(_confirmed(
                                                    f"Delete {chosen_game}")):
                                                games = (
                                                    DB_Calls.delete_game_now(
                                                        cur, table,
                                                        chosen_game, games))
                                        else:
                                            break
                                elif(wishlist_option ==
                                     WishlistGameOptions.SEARCH_GAME.value):
                                    while(True):
                                        game_name = _get_input(
                                            "Enter name of game")
                                        if(game_name):
                                            if(chosen_wishlist ==
                                               WishlistOptions.PC.value):
                                                url = PC.search_url(game_name)
                                                if(_confirmed(f"Open {url}")):
                                                    _open_url(url)
                                            else:
                                                url = PS.search_url(game_name)
                                                if(_confirmed(f"Open {url}")):
                                                    _open_url(url)
                                        else:
                                            break
                                else:
                                    break
                            else:
                                break
                    else:
                        break
            else:
                break
        else:
            break


def _choose_option(_options):
    """Rofi window to select what category of games you want to browse.

    :param options: the options to show to the user
    :type options:  enum
    :return:        the chosen category or None if nothing is chosen
    :rtype:         str or None
    """
    options = ""
    rows = 0
    for val in _options:
        options += val.value
        rows += 1
    category = subprocess.run(["/usr/bin/rofi", "-dmenu", "-p", "", "-lines",
                               f"{rows}", "-columns", "1"],
                              input=str.encode(f"{options}", encoding="UTF-8"),
                              stdout=subprocess.PIPE, shell=False)
    if(category.returncode > 0):
        return None
    return category.stdout.decode("UTF-8")


def _choose_game(category, games, title_lengths):
    """Rofi window to select the game you want to see more about.

    :param category:      the category you have chosen
    :type category:       str
    :param games:         dictionary with list of each category's games
    :type games:          dict
    :param title_lengths: dictionary with each category's longest title
    :type title_lengths:  dict
    :return:              the chosen game
    :rtype:               str
    """
    _GO_UP = ""
    _ADDON = 18

    rofi_string = _GO_UP
    longest_title = 0
    if(category == Categories.TOP_PC.value):
        _table = DB_Tables.TOP_PC.value
        longest_title = title_lengths[_table]
        rofi_string = _form_pc_string(
            rofi_string, games[_table], longest_title)
    elif(category == Categories.TOP_PS.value):
        _table = DB_Tables.TOP_PS.value
        longest_title = title_lengths[_table]
        rofi_string = _form_ps_string(
            rofi_string, games[_table], longest_title)
    elif(category == Categories.PC_WISHLIST.value or category ==
         WishlistOptions.PC.value):
        _table = DB_Tables.PC_WISHLIST.value
        longest_title = title_lengths[_table]
        rofi_string = _form_pc_string(
            rofi_string, games[_table], longest_title)
    elif(category == Categories.PS_WISHLIST.value or category ==
         WishlistOptions.PS.value):
        _table = DB_Tables.PS_WISHLIST.value
        longest_title = title_lengths[_table]
        rofi_string = _form_ps_string(
            rofi_string, games[_table], longest_title)
    else:
        return None, None
    chosen_game = subprocess.run(["/usr/bin/rofi", "-dmenu", "-p", "",
                                  "-lines", "12", "-columns", "2", "-width",
                                 f"-{longest_title*2+_ADDON}"],
                                 stdout=subprocess.PIPE,
                                 input=str.encode(
                                     rofi_string, encoding="UTF-8"),
                                 shell=False)
    if(chosen_game.returncode == 0):
        chosen_game = chosen_game.stdout.decode("UTF-8").split("$")[0].rstrip()
    else:
        chosen_game = None
    return chosen_game, _table


def _get_input(prompt):
    """A rofi prompt to get user input.

    :param prompt: the string that represent's what to prompt for
    :type prompt:  str
    :return:       the string that was entered or None if nothing entered
    :rtype:        str or None
    """
    choice = subprocess.run(["/usr/bin/rofi", "-dmenu", "-p",
                            f"{prompt}", "-lines", "2", "-columns", "1"],
                            stdout=subprocess.PIPE, shell=False)
    if(choice.returncode == 0):
        return choice.stdout.decode("UTF-8")
    return None


def _confirmed(prompt):
    """Rofi window confirming whether or not you want to open the link.

    :param prompt: the prompt that you want to get confirmation for
    :type prompt:  str
    :return:       True if you chose Yes, False otherwise
    :rtype:        bool
    """
    yes = "Yes\n"
    no = "No\n"
    choice = subprocess.run(["/usr/bin/rofi", "-dmenu", "-p", f"{prompt}",
                             "-lines", "2", "-columns", "1"], input=str.encode(
                            f"{yes}{no}", encoding="UTF-8"),
                            stdout=subprocess.PIPE, shell=False
                            ).stdout.decode("UTF-8")
    return (choice == yes)


def _open_url(url):
    """Opens the given url with webbrowser.

    :param url: url to be opened
    :type url: str
    """
    webbrowser.open_new_tab(url)


def _form_pc_string(rofi_string, games, longest_title):
    """Format the PC game deals into nice format for rendering with rofi.

    :param rofi_string:   the string to become the list of games
    :type rofi_string:    str
    :param games:         the games to add to the string
    :type games:          list
    :param longest_title: the longest title in this collection of games
    :type longest_title:  int
    :return:              the string of games to render in the rofi window
    :rtype:               str
    """
    for game in games:
        rofi_string += (
            f"{_stretch_string(game[DB_Indices.TITLE.value], longest_title)}"
            + f" ${game[DB_Indices.SALE_PRICE.value]:.2f}\n")
    return rofi_string


def _form_ps_string(rofi_string, games, longest_title):
    """Format the PC game deals into nice format for rendering with rofi.

    :param rofi_string:   the string to become the list of games
    :type rofi_string:    str
    :param games:         the games to add to the string
    :type games:          list
    :param longest_title: the longest title in this collection of games
    :type longest_title:  int
    :return:              the string of games to render in the rofi window
    :rtype:               str
    """
    for game in games:
        if(game[DB_Indices.SALE_PRICE.value] == PS.ps_plus_price()):
            rofi_string += (
                f"""{_stretch_string(
                    game[DB_Indices.TITLE.value], longest_title)}"""
                + " $PS+")
        else:
            rofi_string += (
                f"""{_stretch_string(
                    game[DB_Indices.TITLE.value], longest_title)}"""
                + f" ${game[DB_Indices.SALE_PRICE.value]:.2f}")
        rofi_string += "\n"
    return rofi_string


def _stretch_string(string, length):
    """Stretch the game title so that each game takes equal space.

    :param string: the string to stretch
    :type string:  str
    :param length: the length that the string needs to be stretched to
    :type length:  int
    :return:       the stretched string
    :rtype:        str
    """
    for _ in range(length-len(string)):
        string += " "
    return string
