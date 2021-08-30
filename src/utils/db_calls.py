#!/usr/bin/python3

'''
  This script contains all the methods pertaining to database interactions.
  ps.py and pc.py both fetch and return the data that this file processes and
  adds to the database.
'''

from datetime import datetime

from src.utils.db_enums import DB_Indices, DB_Columns, DB_Tables


class DB_Calls:
    @staticmethod
    def get_data(cur, table):
        """Get all the data from the specified table, ordering the results by
           sale_price, cheapest to priciest.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to get the data from
        :type table:  str
        :return:      returns all of the table's data orders by sale_price
                      ascending
        :rtype:       list
        """
        top_pc_rq = """SELECT * FROM TOP_PC ORDER BY
                                sale_price ASC"""
        top_ps_rq = """SELECT * FROM TOP_PS ORDER BY
                                sale_price ASC"""
        pc_wishlist_rq = """SELECT * FROM PC_WISHLIST ORDER BY
                                sale_price ASC"""
        ps_wishlist_rq = """SELECT * FROM PS_WISHLIST ORDER BY
                                sale_price ASC"""
        try:
            if(table == DB_Tables.TOP_PC.value):
                return_query = top_pc_rq
            elif(table == DB_Tables.TOP_PS.value):
                return_query = top_ps_rq
            elif(table == DB_Tables.PC_WISHLIST.value):
                return_query = pc_wishlist_rq
            elif(table == DB_Tables.PS_WISHLIST.value):
                return_query = ps_wishlist_rq
            return cur.execute(return_query).fetchall()
        except Exception:
            if(table == DB_Tables.TOP_PC.value):
                query = """CREATE TABLE TOP_PC(
                        title TEXT NOT NULL UNIQUE,
                        full_price REAL,
                        sale_price REAL,
                        cover_image TEXT,
                        url TEXT NOT NULL UNIQUE,
                        gid INTEGER UNIQUE,
                        update_time TEXT,
                        title_length INTEGER)"""
                return_query = top_pc_rq
            elif(table == DB_Tables.TOP_PS.value):
                query = """CREATE TABLE TOP_PS(
                        title TEXT NOT NULL UNIQUE,
                        full_price REAL,
                        sale_price REAL,
                        cover_image TEXT,
                        url TEXT NOT NULL UNIQUE,
                        gid INTEGER UNIQUE,
                        update_time TEXT,
                        title_length INTEGER)"""
                return_query = top_ps_rq
            elif(table == DB_Tables.PC_WISHLIST.value):
                query = """CREATE TABLE PC_WISHLIST(
                        title TEXT NOT NULL UNIQUE,
                        full_price REAL,
                        sale_price REAL,
                        cover_image TEXT,
                        url TEXT NOT NULL UNIQUE,
                        gid INTEGER UNIQUE,
                        update_time TEXT,
                        title_length INTEGER)"""
                return_query = pc_wishlist_rq
            elif(table == DB_Tables.PS_WISHLIST.value):
                query = """CREATE TABLE PS_WISHLIST(
                        title TEXT NOT NULL UNIQUE,
                        full_price REAL,
                        sale_price REAL,
                        cover_image TEXT,
                        url TEXT NOT NULL UNIQUE,
                        gid INTEGER UNIQUE,
                        update_time TEXT,
                        title_length INTEGER)"""
                return_query = ps_wishlist_rq
            cur.execute(query)
            return cur.execute(return_query).fetchall()

    @staticmethod
    def add_top_deals(cur, table, existing_games, new_games):
        """Add the top deals to the database.

        :param cur:            database cursor
        :type cur:             cursor
        :param table:          the table to update the deals of
        :type table:           str
        :param existing_games: a list of games that are already in the database
                               and therefore will be updated
        :type existing_games:  list
        :param new_games:      a list of games that are not already in the
                               database and therefore will be inserted
        :type new_games:       list
        """
        unmatched_titles = []
        matched_titles = []
        # When adding top deals, we need to remove the games that are no
        # longer a "top deal"
        for existing_game in existing_games:
            matched = False
            for new_game in new_games:
                if(existing_game[DB_Indices.GID.value] ==
                   new_game[DB_Columns.GID.value]):
                    matched = True
                    matched_titles.append(existing_game[DB_Indices.GID.value])
                    break
            if(not matched):
                # append it to the list of titles that we will delete
                unmatched_titles.append(existing_game[DB_Indices.TITLE.value])

        # Delete the games that aren't found in the api response anymore
        for title in unmatched_titles:
            DB_Calls.delete_game_with_title(cur, table, title)

        # Update the remainder of the games that are already present, add the
        # games that are new entries to the database.
        DB_Calls.add_games(cur, table, new_games, matched_titles)

    @staticmethod
    def add_games(cur, table, games, games_to_update=None):
        """Get all the data from the specified table, ordering the results by
           sale_price, cheapest to priciest.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to get the data from
        :type table:  str
        :return:      returns all of the table's data orders by sale_price
                      ascending
        :rtype:       list
        """
        if(table == DB_Tables.TOP_PC.value):
            query = """SELECT * FROM TOP_PC WHERE
                                gid=?"""
        elif(table == DB_Tables.TOP_PS.value):
            query = """SELECT * FROM TOP_PS WHERE
                                gid=?"""
        elif(table == DB_Tables.PC_WISHLIST.value):
            query = """SELECT * FROM PC_WISHLIST WHERE
                                gid=?"""
        elif(table == DB_Tables.PS_WISHLIST.value):
            query = """SELECT * FROM PS_WISHLIST WHERE
                                gid=?"""
        if(games_to_update is None):
            for game in games:
                if(cur.execute(query, (game[DB_Columns.GID.value], )
                               ).fetchone()):
                    DB_Calls._update_game(cur, table, game)
                else:
                    DB_Calls._add_game(cur, table, game)
        else:
            for game in games:
                if(game[DB_Columns.GID.value] in games_to_update):
                    DB_Calls._update_game(cur, table, game)
                else:
                    DB_Calls._add_game(cur, table, game)

    @staticmethod
    def game_exists(cur, table, id_=None, url=None):
        """Determines if a game with the given id is in the database.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to check game id for
        :type table:  str
        :param id_:    the id to search table for
        :type id_:     int
        :return: [description]
        :rtype: [type]
        """
        if(url):
            parameter = url
            if(table == DB_Tables.TOP_PC.value):
                query = """SELECT * FROM TOP_PC WHERE
                                url=?"""
            elif(table == DB_Tables.TOP_PS.value):
                query = """SELECT * FROM TOP_PS WHERE
                                url=?"""
            elif(table == DB_Tables.PC_WISHLIST.value):
                query = """SELECT * FROM PC_WISHLIST WHERE
                                url=?"""
            elif(table == DB_Tables.PS_WISHLIST.value):
                query = """SELECT * FROM PS_WISHLIST WHERE
                                url=?"""
        elif(id_):
            parameter = id_
            if(table == DB_Tables.TOP_PC.value):
                query = """SELECT * FROM TOP_PC WHERE
                                gid=?"""
            elif(table == DB_Tables.TOP_PS.value):
                query = """SELECT * FROM TOP_PS WHERE
                                gid=?"""
            elif(table == DB_Tables.PC_WISHLIST.value):
                query = """SELECT * FROM PC_WISHLIST WHERE
                                gid=?"""
            elif(table == DB_Tables.PS_WISHLIST.value):
                query = """SELECT * FROM PS_WISHLIST WHERE
                                gid=?"""
        if(cur.execute(query, (parameter, )).fetchone()):
            return True
        return False

    @staticmethod
    def delete_game_with_title(cur, table, title):
        """Delete game with given title from the database.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to delete the title from
        :type table:  str
        :param title: the title of the game to delete
        :type title:  str
        """
        if(table == DB_Tables.TOP_PC.value):
            query = """DELETE FROM TOP_PC WHERE
                     title=?"""
        elif(table == DB_Tables.TOP_PS.value):
            query = """DELETE FROM TOP_PS WHERE
                     title=?"""
        elif(table == DB_Tables.PC_WISHLIST.value):
            query = """DELETE FROM PC_WISHLIST WHERE
                     title=?"""
        elif(table == DB_Tables.PS_WISHLIST.value):
            query = """DELETE FROM PS_WISHLIST WHERE
                     title=?"""
        cur.execute(query, (title, ))

    @staticmethod
    def delete_game_with_id(cur, table, id_):
        """Delete game with given id from the database.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to delete the id from
        :type table:  str
        :param id_:    the id to delete from the table
        :type id_:     int
        """
        if(table == DB_Tables.TOP_PC.value):
            query = """DELETE FROM TOP_PC WHERE
                     gid=?"""
        elif(table == DB_Tables.TOP_PS.value):
            query = """DELETE FROM TOP_PS WHERE
                     gid=?"""
        elif(table == DB_Tables.PC_WISHLIST.value):
            query = """DELETE FROM PC_WISHLIST WHERE
                     gid=?"""
        elif(table == DB_Tables.PS_WISHLIST.value):
            query = """DELETE FROM PS_WISHLIST WHERE
                     gid=?"""
        cur.execute(query, (id_, ))

    @staticmethod
    def delete_game_now(cur, table, title, games):
        """Delete game with given title from database and games list.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to delete game from
        :type table:  str
        :param title: the title of the game to delete
        :type title:  str
        :param games: the games list holding the title
        :type games:  list
        :return:      the list of games without the now removed game
        :rtype:       list
        """
        for index, game in enumerate(games[table]):
            if(game[DB_Indices.TITLE.value] == title):
                del games[table][index]
                DB_Calls.delete_game_with_title(cur, table, title)
                break
        return games

    @staticmethod
    def get_game_url(cur, table, title):
        """Fetch a game's url given the title and table of the game.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to search
        :type table:  str
        :param title: the title of the game to get url from
        :type title:  str
        :return:      the url of the game if the title exists, otherwise None
        :rtype:       str or None
        """
        url = cur.execute(f"""SELECT {DB_Columns.URL.value} FROM {table} WHERE
                           {DB_Columns.TITLE.value}=?""", (title, )).fetchone()
        if(url):
            return url[0]
        return None

    @staticmethod
    def get_longest_title(cur, table):
        """Get the longest title from the given table, used for formatting the
           games for rendering in the rofi window.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to get longest title from
        :type table:  str
        :return:      the longest title from the table
        :rtype:       int
        """
        length = cur.execute(
            f"""SELECT {DB_Columns.TITLE_LENGTH.value} FROM {table} ORDER BY
             {DB_Columns.TITLE_LENGTH.value} DESC""").fetchone()
        if(length):
            return length[0]
        return 10

    @staticmethod
    def needs_updating(cur, table, update_delay):
        """Determines if the table needs updating, depends on the value of
           update_delay otherwise it uses the default update_delay.

        :param cur:          database cursor
        :type cur:           cursor
        :param table:        the table to check
        :type table:         str
        :param update_delay: the time that must pass before needing to update
        :type date_str:      datetime
        :return:             True if it needs updating, False otherwise
        :rtype:              bool
        """
        try:
            past_time = DB_Calls._str_to_dt(cur.execute(
                f"""SELECT {DB_Columns.UPDATE_TIME.value} FROM
                    {table}""").fetchone()[0])
        except Exception:
            return True
        return ((datetime.now() - past_time) > update_delay)

    @staticmethod
    def wishlist_needs_updating(cur, table, update_delay):
        """Determines which individual games from the table need updating.

        :param cur:          database cursor
        :type cur:           cursor
        :param table:        the table to check
        :type table:         str
        :param update_delay: the time that must pass before needing to update
        :type date_str:      datetime
        :return:             True if it needs updating, False otherwise
        :rtype:              bool
        """
        if(table == DB_Tables.PC_WISHLIST.value):
            try:
                games = cur.execute(
                    f"""SELECT {DB_Columns.GID.value},
                        {DB_Columns.UPDATE_TIME.value} FROM
                        {table}""").fetchall()
            except Exception:
                return []
        elif(table == DB_Tables.PS_WISHLIST.value):
            try:
                games = cur.execute(
                    f"""SELECT {DB_Columns.URL.value},
                        {DB_Columns.UPDATE_TIME.value} FROM
                        {table}""").fetchall()
            except Exception:
                return []
        games_to_update = []
        for game in games:
            if((datetime.now() - DB_Calls._str_to_dt(game[1])) > update_delay):
                games_to_update.append(game[0])
        return games_to_update

    @staticmethod
    def _str_to_dt(date_str):
        """Convert a date string into a valid datetime object.

        :param date_str: a string representation of datetime to convert
        :type date_str:  str
        :return:         a datetime object
        :rtype:          datetime
        """
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")

    @staticmethod
    def _add_game(cur, table, game):
        """Add the game to the given table.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to add the game to
        :type table:  str
        :param game:  the game dictionary to add to the table
        :type game:   dict
        """
        cur.execute(f"""INSERT INTO {table} VALUES(
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
    def _update_game(cur, table, game):
        """Update the game in the given table.

        :param cur:   database cursor
        :type cur:    cursor
        :param table: the table to update the game in
        :type table:  str
        :param game:  the game dictionary to update in the table
        :type game:   dict
        """
        cur.execute(f"""UPDATE {table} SET
                    {DB_Columns.FULL_PRICE.value}=?,
                    {DB_Columns.SALE_PRICE.value}=?,
                    {DB_Columns.URL.value}=?,
                    {DB_Columns.UPDATE_TIME.value}=?
                    WHERE {DB_Columns.GID.value}=?""",
                    (game[DB_Columns.FULL_PRICE.value],
                        game[DB_Columns.SALE_PRICE.value],
                        game[DB_Columns.URL.value],
                        datetime.now(),
                        game[DB_Columns.GID.value]))
