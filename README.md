# PolybarGameDeals
This script provides an all-in-one place for PC and Playstation deals. I built this to use for a [Polybar](https://github.com/polybar/polybar) module, and [Rofi](https://github.com/davatorium/rofi) seemed like a good way to render and interact with the data, but feel free to do whatever you want with it.

## Dependencies
  - Programs
    - Python 3
    - Rofi
    - A browser (default Firefox)
  - Python
    - Beautifulsoup4

## Data Sources
  - PC Deals: [cheapshark.com](https://www.cheapshark.com/) (API)
  - Playstation Deals: [psdeals.net](https://psdeals.net/) (Scraped)
___
## How it works
All deals are stored in a SQLite database. Data requests are only made if a certain amount of time has passed since the last request. This delay makes the program run faster and is also important because PSDeals doesn't offer an API, so excessive requests to their servers should be avoided.

To run it, just download or clone this repository, go to the project's location in a terminal, make sure main.[]()py is executable and run it with:
```bash
./main.py
```
or
```bash
python3 main.py
```
The database will be automatically created and populated, just give it some time to fetch the data.
___
## Modification
### Don't want rofi?
Feel free to tweak this however you want. For instance, if you don't want to use Rofi then you need only replace the following line in main.[]()py:
```python
launch_rofi(cur, games)
```
with whatever you want to do with the data. 

### Game price is running off the rofi menu?
One thing you will need to probably change is the spacing between the game title and the price of the game. The price of the game may not be visible at all with the default configuration, so go into utils.[]()py and find and replace all instances of:
```bash
45s
```
with some value like:
```bash
20s
```
until you get a string length that's desirable for your monitor.
___
## Notes
  - All PC links go to [cheapshark.com](https://www.cheapshark.com/) and will be redirected to the store with the best deal.
  - All Playstation links are scraped from [psdeals.net](https://psdeals.net/) and when chosen will open a link directly to their website. Because the data is scraped from their website, there is a sleeping period between each page request. So, if it's taking a while to run, it's just making the requests and sleeping for a bit.
