# PolybarGameDeals

<!-- ![](https://img.shields.io/github/repo-size/nkayp/PolybarGameDeals.svg?label=Repo%20size) -->
![](https://img.shields.io/tokei/lines/github/nkayp/PolybarGameDeals)
[![CodeFactor](https://www.codefactor.io/repository/github/nkayp/polybargamedeals/badge)](https://www.codefactor.io/repository/github/nkayp/polybargamedeals)
![](https://img.shields.io/github/license/nkayp/PolybarGameDeals)

This script provides an all-in-one place for PC and Playstation deals. I built this to use for a [Polybar](https://github.com/polybar/polybar) module, and [Rofi](https://github.com/davatorium/rofi) seemed like a good way to render and interact with the data, but feel free to do whatever you want with it.

## Dependencies
  - Rofi
  - A browser
  - Python 3
    - beautifulsoup4
    - requests

## Data Sources
  - PC Deals: [cheapshark.com](https://www.cheapshark.com/) (API)
  - Playstation Deals: [psdeals.net](https://psdeals.net/) (Scraped)
## How it works
All deals are stored in a SQLite database. Data requests are only made if a certain amount of time has passed since the last request. This delay makes the program run faster and is also important because PSDeals doesn't offer an API, so excessive requests to their servers should be avoided.

To run it, just download or clone this repository, go to the project's location in a terminal and run:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Then make sure main.[]()py is executable and run it with:
```bash
python main.py
```
The database will be automatically created and populated, just give it some time to fetch the data.
## Arguments
```bash
# only open a rofi window, do not check for updates
-r, --rofi
```
```bash
# only check for updates, do not open a rofi window
-s, --silent
```
<!-- ```bash
# show prices and deals available for Playstation Plus subscribers
-p, --ps-plus
``` -->
```bash
# specify the max price for top pc deals, defaults to 15
--pc-max PC_MAX
```
```bash
# to add Playstation games to your wishlist specify the urls following the -ps command
--ps PS [PS ...]
```
```bash
# to add PC games to your wishlist specify the ids following the -pc command
--pc PC [PC ...]
```

## Modification
### Want to do something else with the data?
Feel free to tweak this however you want. For instance, if you don't want to use Rofi then you need only replace the following lines in main.[]()py with whatever you want to do with the data:
```python
if(args.rofi or not args.silent):
    launch_rofi(cur, games, title_lengths)
```

## Notes
  - All PC links go to [cheapshark.com](https://www.cheapshark.com/) and will be redirected to the store with the best deal.
  - All Playstation links are scraped from [psdeals.net](https://psdeals.net/) and when chosen will open a link directly to their website. Because the data is scraped from their website, there is a sleeping period between each page request. So, if it's taking a while to run, it's just making the requests and sleeping for a bit.
