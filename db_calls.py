#!/usr/bin/python3

from datetime import datetime
from enum import Enum

class Tables(Enum):
  TOP_PC = "TOP_PC"
  YOUR_PC = "YOUR_PC"
  TOP_PS = "TOP_PS"
  YOUR_PS = "YOUR_PS"


class DB_Calls:
  ############################
  '''   "PUBLIC" METHODS   '''
  ############################
  @staticmethod
  def get_data(cur, table):
    try:
      return cur.execute(f"""SELECT * FROM {table};""")
    except Exception:
      print(f"Creating table {table}...")
      cur.execute(f"""CREATE TABLE {table}(title TEXT NOT NULL UNIQUE, full_price REAL, sale_price REAL, cover_image TEXT, url TEXT NOT NULL UNIQUE, update_time TEXT);""")
      return cur.execute(f"""SELECT * FROM {table};""").fetchall()

  @staticmethod
  def add_data(cur, table, game):
    ''' Becuase we can, we should make sure there aren't gonna be SQL injections   '''
    cur.execute(f"""INSERT INTO {table} VALUES(?, ?, ?, ?, ?, ?)""", (game['title'], game['full_price'], game['sale_price'], game['cover_image'], game['url'], datetime.now()))



  #############################
  '''   "PRIVATE" METHODS   '''
  #############################
  @staticmethod
  def __str_to_dt(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f").now()
