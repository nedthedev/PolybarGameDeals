# PolybarGameDeals
This script provides an all-in-one place for PC and Playstation deals. I built this to use for a [Polybar](https://github.com/polybar/polybar) module, and [Rofi](https://github.com/davatorium/rofi) seemed like a good way to render and interact with the data, but feel free to do whatever you want with it.

## Dependencies
  - Programs
    - Python 3
    - rofi
    - A browser (default Firefox)
  - Python
    - beautifulsoup4

## Data Sources
  - PC Deals: [cheapshark.com](https://www.cheapshark.com/) (API)
  - Playstation Deals: [psdeals.net](https://psdeals.net/) (Scraped)

## How it works
All deals are stored in a SQLite database. Data requests are only made if a certain amount of time has passed since the last request. This delay makes the program run faster and is also important because PSDeals doesn't offer an API, so excessive requests to their servers should be avoided.

## Modification
Feel free to tweak this however you want. For instance, if you don't want to use Rofi, then you need only replace the following line:
```python
launch_rofi(cur, games)
```
with whatever you want to do with the data. 

## Notes
  - All PC links go to [cheapshark.com](https://www.cheapshark.com/) and will be redirected to the store with the best deal.
  - All Playstation links are scraped from [psdeals.net](https://psdeals.net/) and when chosen will open a link directly to their website. Because the data is scraped from their website, there is a sleeping period between each page request. So, if it's taking a while to run, it's just making the requests and sleeping for a bit.
