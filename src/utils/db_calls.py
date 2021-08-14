#!/usr/bin/python3

'''
  This script contains all the methods pertaining to database interactions.
  ps.py and pc.py both fetch and return the data that this file processes and
  adds to the database.
'''

from datetime import datetime, timedelta

from .db_enums import DB_Indices, DB_Columns, DB_Tables
from ..platforms.pc import PC
from ..platforms.ps import PS


class DB_Calls:
    #####################
    '''   VARIABLES   '''
    #####################
    ''' The default delay before updating the top deals '''
    _UPDATE_DELAY = timedelta(seconds=0, minutes=0, hours=12, days=0)

    ############################
    '''   "PUBLIC" METHODS   '''
    ############################
    ''' A simple function to fetch all the data from the given table. If the
    table doesn't exist then it will be created. '''
    @staticmethod
    def get_data(cur, table):
        if(table == DB_Tables.TOP_PC.value):
            try:
                cur.execute("""SELECT SALE_PRICE FROM TOP_PC""")
            except Exception:
                cur.execute(""" CREATE TABLE TOP_PC(
                    title TEXT NOT NULL UNIQUE,
                    full_price REAL,
                    sale_price REAL,
                    cover_image TEXT,
                    url TEXT NOT NULL UNIQUE,
                    gid INTEGER UNIQUE,
                    update_time TEXT,
                    title_length INTEGER)""")
            return cur.execute("""SELECT * FROM TOP_PC
                               ORDER BY sale_price ASC""").fetchall()
        elif(table == DB_Tables.TOP_PS.value):
            try:
                cur.execute("""SELECT SALE_PRICE FROM TOP_PS""")
            except Exception:
                cur.execute("""CREATE TABLE TOP_PS(
                    title TEXT NOT NULL UNIQUE,
                    full_price REAL,
                    sale_price REAL,
                    cover_image TEXT,
                    url TEXT NOT NULL UNIQUE,
                    gid INTEGER UNIQUE,
                    update_time TEXT,
                    title_length INTEGER)""")
            return cur.execute("""SELECT * FROM TOP_PS
                               ORDER BY sale_price ASC""").fetchall()
        elif(table == DB_Tables.PC_WISHLIST.value):
            try:
                cur.execute("""SELECT SALE_PRICE FROM PC_WISHLIST""")
            except Exception:
                cur.execute("""CREATE TABLE TOP_PS(
                    title TEXT NOT NULL UNIQUE,
                    full_price REAL,
                    sale_price REAL,
                    cover_image TEXT,
                    url TEXT NOT NULL UNIQUE,
                    gid INTEGER UNIQUE,
                    update_time TEXT,
                    title_length INTEGER)""")
            return cur.execute("""SELECT * FROM PC_WISHLIST
                               ORDER BY sale_price ASC""").fetchall()
        elif(table == DB_Tables.PS_WISHLIST.value):
            try:
                cur.execute("""SELECT SALE_PRICE FROM PS_WISHLIST""")
            except Exception:
                cur.execute("""CREATE TABLE TOP_PS(
                    title TEXT NOT NULL UNIQUE,
                    full_price REAL,
                    sale_price REAL,
                    cover_image TEXT,
                    url TEXT NOT NULL UNIQUE,
                    gid INTEGER UNIQUE,
                    update_time TEXT,
                    title_length INTEGER)""")
            return cur.execute("""SELECT * FROM PS_WISHLIST
                               ORDER BY sale_price ASC""").fetchall()

    ''' Add top deals to the database. Since top deals will time out and not
        exist anymore, we need to check if games in the database need to
        updated or removed. '''
    @staticmethod
    def add_top_deals(cur, table, existing_games, new_games):
        ''' When adding top deals, we need to remove the games that are no
            longer a "top deal" '''
        unmatched_titles = []
        for existing_game in existing_games:
            matched = False
            for new_game in new_games:
                if(existing_game[DB_Indices.TITLE.value] ==
                   new_game[DB_Columns.TITLE.value]):
                    matched = True
                    break
            if(not matched):
                ''' append it to the list of titles that we will delete '''
                unmatched_titles.append(existing_game[DB_Indices.TITLE.value])

        ''' Delete the games that aren't found in the api response anymore '''
        for title in unmatched_titles:
            DB_Calls.delete_game_with_title(cur, table, title)

        ''' Update the remainder of the games that are already present, add the
        games that are new entries to the database. '''
        if(table == DB_Tables.TOP_PC.value):
            for game in new_games:
                if(cur.execute("""SELECT * FROM TOP_PC WHERE TITLE=?""",
                   (game[DB_Columns.TITLE.value], )).fetchone()):
                    cur.execute("""UPDATE TOP_PC SET
                                sale_price=?,
                                url=?,
                                update_time=?
                                WHERE TITLE=?""",
                                (game[DB_Columns.SALE_PRICE.value],
                                    game[DB_Columns.URL.value],
                                    datetime.now(),
                                    game[DB_Columns.TITLE.value]))
                else:
                    cur.execute("""INSERT INTO TOP_PC VALUES(
                                   ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (game[DB_Columns.TITLE.value],
                                    game[DB_Columns.FULL_PRICE.value],
                                    game[DB_Columns.SALE_PRICE.value],
                                    game[DB_Columns.COVER_IMAGE.value],
                                    game[DB_Columns.URL.value],
                                    game[DB_Columns.GID.value],
                                    datetime.now(),
                                    len(game[DB_Columns.TITLE.value])))
        elif(table == DB_Tables.TOP_PS.value):
            for game in new_games:
                if(cur.execute("""SELECT * FROM TOP_PS WHERE TITLE=?""",
                               (game[DB_Columns.TITLE.value], )).fetchone()):
                    cur.execute("""UPDATE TOP_PS
                                SET sale_price=?,
                                url=?,
                                update_time=?
                                WHERE TITLE=?""",
                                (game[DB_Columns.SALE_PRICE.value],
                                    game[DB_Columns.URL.value],
                                    datetime.now(),
                                    game[DB_Columns.TITLE.value]))
                else:
                    cur.execute("""INSERT INTO TOP_PS VALUES(
                                ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (game[DB_Columns.TITLE.value],
                                    game[DB_Columns.FULL_PRICE.value],
                                    game[DB_Columns.SALE_PRICE.value],
                                    game[DB_Columns.COVER_IMAGE.value],
                                    game[DB_Columns.URL.value],
                                    game[DB_Columns.GID.value],
                                    datetime.now(),
                                    len(game[DB_Columns.TITLE.value])))

    @staticmethod
    def game_exists(cur, table, cls, id):
        if(table == DB_Tables.PC_WISHLIST.value):
            if(cls.is_valid(id)):
                if(cur.execute("""SELECT * FROM PC_WISHLIST
                               WHERE gid=? OR url=?""", (id, id)).fetchone()):
                    return True
        elif(table == DB_Tables.PS_WISHLIST.value):
            if(cls.is_valid(id)):
                if(cur.execute("""SELECT * FROM PS_WISHLIST
                               WHERE gid=? OR url=?""", (id, id)).fetchone()):
                    return True
        return False

    ''' Delete game with given title from the database '''
    @staticmethod
    def delete_game_with_title(cur, table, title):
        if(table == DB_Tables.TOP_PC.value):
            cur.execute("""DELETE FROM TOP_PC WHERE TITLE=?""", (title, ))
        elif(table == DB_Tables.TOP_PS.value):
            cur.execute("""DELETE FROM TOP_PS WHERE TITLE=?""", (title, ))
        elif(table == DB_Tables.PC_WISHLIST.value):
            cur.execute("""DELETE FROM PC_WISHLIST WHERE TITLE=?""", (title, ))
        elif(table == DB_Tables.PS_WISHLIST.value):
            cur.execute("""DELETE FROM PS_WISHLIST WHERE TITLE=?""", (title, ))

    @staticmethod
    def delete_game_with_id(cur, table, id):
        if(table == DB_Tables.TOP_PC.value):
            cur.execute("""DELETE FROM TOP_PC WHERE gid=?""", (id, ))
        elif(table == DB_Tables.TOP_PS.value):
            cur.execute("""DELETE FROM TOP_PS WHERE gid=?""", (id, ))
        elif(table == DB_Tables.PC_WISHLIST.value):
            cur.execute("""DELETE FROM PC_WISHLIST WHERE gid=?""", (id, ))
        elif(table == DB_Tables.PS_WISHLIST.value):
            cur.execute("""DELETE FROM PS_WISHLIST WHERE gid=?""", (id, ))

    ''' Delete game with given title from the database and the list of games
      This function is used exclusively to delete games through the rofi
      prompt '''
    @staticmethod
    def delete_game_now(cur, table, title, games):
        if(table == DB_Tables.TOP_PC.value):
            for index, game in enumerate(games[table]):
                if(game[DB_Indices.TITLE.value] == title):
                    del games[table][index]
                    cur.execute(
                        """DELETE FROM TOP_PC WHERE TITLE=?""", (title, ))
                    break
        elif(table == DB_Tables.TOP_PS.value):
            for index, game in enumerate(games[table]):
                if(game[DB_Indices.TITLE.value] == title):
                    del games[table][index]
                    cur.execute(
                        """DELETE FROM TOP_PS WHERE TITLE=?""", (title, ))
                    break
        elif(table == DB_Tables.PC_WISHLIST.value):
            for index, game in enumerate(games[table]):
                if(game[DB_Indices.TITLE.value] == title):
                    del games[table][index]
                    cur.execute(
                        """DELETE FROM PC_WISHLIST WHERE TITLE=?""", (title, ))
                    break
        elif(table == DB_Tables.PS_WISHLIST.value):
            for index, game in enumerate(games[table]):
                if(game[DB_Indices.TITLE.value] == title):
                    del games[table][index]
                    cur.execute(
                        """DELETE FROM PS_WISHLIST WHERE TITLE=?""", (title, ))
                    break
        return games

    ''' Called when wanting to add new wishlist PC games '''
    @staticmethod
    def add_pc_games(cur, table, ids):
        time = datetime.now()
        id_string = ""
        update_ids = []
        for index, id in enumerate(ids):
            if(PC.is_valid(id)):
                ''' Form the valid string of ids for fetching data from api
                    with one request '''
                if(not index == len(ids)-1):
                    id_string += f"{id},"
                else:
                    id_string += f"{id}"
                ''' If it is in the database then we will update '''
                if(cur.execute("""SELECT update_time FROM PC_WISHLIST
                               WHERE gid=?""", (id, )).fetchone()):
                    update_ids.append(id)
        games = PC.get_wishlist_games(id_string)
        if(games):
            for game in games:
                ''' If it is a game that we needed to update '''
                if(game[DB_Columns.GID.value] in update_ids):
                    cur.execute("""UPDATE PC_WISHLIST SET
                                full_price=?,
                                sale_price=?,
                                url=?,
                                update_time=?
                                WHERE gid=?""",
                                (game[DB_Columns.FULL_PRICE.value],
                                    game[DB_Columns.SALE_PRICE.value],
                                    game[DB_Columns.URL.value],
                                    time,
                                    game[DB_Columns.GID.value]))
                else:
                    cur.execute("""INSERT INTO PC_WISHLIST
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                                (game[DB_Columns.TITLE.value],
                                    game[DB_Columns.FULL_PRICE.value],
                                    game[DB_Columns.SALE_PRICE.value],
                                    game[DB_Columns.COVER_IMAGE.value],
                                    game[DB_Columns.URL.value],
                                    game[DB_Columns.GID.value],
                                    time,
                                    len(game[DB_Columns.TITLE.value])))
        return games

    ''' Called when wanting to add new wishlist Playstation games '''
    @staticmethod
    def add_ps_games(cur, table, urls):
        time = datetime.now()
        games = []
        existing_games = []
        for index, url in enumerate(urls):
            gid = PS.get_gid(url)
            if(PS.is_valid(url)):
                ''' If the game already exists in the database then we need
                    only update '''
                if(cur.execute("""SELECT url, update_time FROM PS_WISHLIST
                               WHERE URL=? OR GID=?""", (url, gid)
                               ).fetchone()):
                    existing_games.append(gid)
                ''' We must fetch the data for every game, because every game
                    provided needs updating '''
                if(index == len(urls)-1):
                    sleep = False
                else:
                    sleep = True
                game = PS.get_your_deals(url, sleep)
                if(game):
                    games.append(game)
        if(games):
            for game in games:
                ''' If it is a game that we needed to update '''
                if(game[DB_Columns.GID.value] in existing_games):
                    cur.execute("""UPDATE PS_WISHLIST SET
                                full_price=?,
                                sale_price=?,
                                update_time=?
                                WHERE GID=?""",
                                (game[DB_Columns.FULL_PRICE.value],
                                    game[DB_Columns.SALE_PRICE.value],
                                    time,
                                    game[DB_Columns.GID.value]))
                else:
                    cur.execute("""INSERT INTO PS_WISHLIST
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                                (game[DB_Columns.TITLE.value],
                                    game[DB_Columns.FULL_PRICE.value],
                                    game[DB_Columns.SALE_PRICE.value],
                                    game[DB_Columns.COVER_IMAGE.value],
                                    game[DB_Columns.URL.value],
                                    game[DB_Columns.GID.value],
                                    time,
                                    len(game[DB_Columns.TITLE.value])))
        return games

    ''' Fetch a game's url given the title and table of the game '''
    @staticmethod
    def get_game_url(cur, table, title):
        if(table == DB_Tables.TOP_PC.value):
            url = cur.execute(
                """SELECT url FROM TOP_PC WHERE TITLE=?""",
                (title, )).fetchone()
        elif(table == DB_Tables.TOP_PS.value):
            url = cur.execute(
                """SELECT url FROM TOP_PS WHERE TITLE=?""",
                (title, )).fetchone()
        elif(table == DB_Tables.PC_WISHLIST.value):
            url = cur.execute(
                """SELECT url FROM PC_WISHLIST WHERE TITLE=?""",
                (title, )).fetchone()
        elif(table == DB_Tables.PS_WISHLIST.value):
            url = cur.execute(
                """SELECT url FROM PS_WISHLIST WHERE TITLE=?""",
                (title, )).fetchone()
        if(url):
            return url[0]
        else:
            return None

    ''' Simple function to get the longest title from the given table '''
    @staticmethod
    def get_longest_title(cur, table):
        if(table == DB_Tables.TOP_PC.value):
            length = cur.execute(
                """SELECT title_length FROM TOP_PC
                ORDER BY title_length DESC""").fetchone()
        elif(table == DB_Tables.TOP_PS.value):
            length = cur.execute(
                """SELECT title_length FROM TOP_PS
                ORDER BY title_length DESC""").fetchone()
        elif(table == DB_Tables.PC_WISHLIST.value):
            length = cur.execute(
                """SELECT title_length FROM PC_WISHLIST
                ORDER BY title_length DESC""").fetchone()
        elif(table == DB_Tables.PS_WISHLIST.value):
            length = cur.execute(
                """SELECT title_length FROM PS_WISHLIST
                ORDER BY title_length DESC""").fetchone()
        if(length):
            return length[0]
        else:
            return 10

    ''' Determine if the top deals need to be updated based on update_delay.
        The function first checks to see if an entry even exists, if one does
        then it will check the elapsed time. '''
    @staticmethod
    def needs_updating(cur, table, update_delay=None):
        if(table == DB_Tables.TOP_PC.value):
            try:
                past_time = DB_Calls._str_to_dt(cur.execute(
                    """SELECT update_time FROM TOP_PC""").fetchone()[0])
            except Exception:
                return True
        elif(table == DB_Tables.TOP_PS.value):
            try:
                past_time = DB_Calls._str_to_dt(cur.execute(
                    """SELECT update_time FROM TOP_PS""").fetchone()[0])
            except Exception:
                return True
        if(not update_delay):
            update_delay = DB_Calls._UPDATE_DELAY
        return ((datetime.now() - past_time) > update_delay)

    ''' Checks and finds all PC wishlist games that need updating '''
    @staticmethod
    def wishlist_needs_updating(cur, table, update_delay=None):
        if(not update_delay):
            update_delay = DB_Calls._UPDATE_DELAY
        if(table == DB_Tables.PC_WISHLIST.value):
            try:
                games = cur.execute(
                    """SELECT gid, update_time FROM PC_WISHLIST""").fetchall()
            except Exception:
                return []
        elif(table == DB_Tables.PS_WISHLIST.value):
            try:
                games = cur.execute(
                    """SELECT url, update_time FROM PS_WISHLIST""").fetchall()
            except Exception:
                return []
        games_to_update = []
        for game in games:
            if((datetime.now() - DB_Calls._str_to_dt(game[1])) > update_delay):
                games_to_update.append(game[0])
        return games_to_update

    #############################
    '''   "PRIVATE" METHODS   '''
    #############################
    ''' Convert a date string into a valid datetime object '''
    @staticmethod
    def _str_to_dt(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
