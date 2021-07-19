import requests

class Game:
  
  ###################
  '''  VARIABLES  '''
  ###################
  _PAGES = 3  # Number of pages to fetch for top deals
  _TOP_DEALS_URL = "https://psprices.com/region-us/collection/biggest-deals?sort=subscribers&ordering=desc&page="   # Root url for the top deals



  #######################
  '''  CLASS METHODS  '''
  #######################
  @classmethod
  def get_top_deals(cls, pages=None):
    print("Fetching best current deals...")
    if(pages == None): pages = cls._PAGES
    data = []
    for _page in range(pages):
      tmp = cls._get_top_deals(f"{cls._TOP_DEALS_URL}{_page+1}")  # Download deals
      if(tmp):  # Check that it isn't None
        data.append(tmp)
    data = cls._clean_data(data)  # Clean / parse the data
    cls._update_db(data)  # Update the database

  @classmethod
  def get_your_deals(cls):
    print("Fetching your deals...")



  ########################
  '''  STATIC METHODS  '''
  ########################
  @staticmethod
  def _get_top_deals(url):
    print("Downloading the top deals...")
    return url
  
  @staticmethod
  def _clean_data(data):
    print("Cleaning data...")

  @staticmethod
  def _update_db(data):
    print("Updating database...")

  @staticmethod
  def _get_top_deals(url):
    r = requests.get(url)
    if(r.status_code == 200):
      return r.json()
    return None

  @staticmethod
  def update_db(data, table):
    print(f"Updating {table} in the db...")