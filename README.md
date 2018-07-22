# Digitec Price Bot

This is a tiny pricecrawler for two online shops [Digitec] and [Galaxus].
The script can be run periodically to track the price fluctuations of certain products.

> digitec and galaxus are online shops from the swiss company [Digitec Galaxus AG]

You can subscribe to the [@digitecdaily](https://t.me/digitecdaily) channel on Telegram which posts the 
digitec offer of the day each morning.

---

### Requirements
- Python 2.7
- HTML-parser BeautifulSoup (bs4)

```bash
sudo pip install bs4
```

---

## Daily Offer

The [`digitec-daily-offer.py`](digitec-daily-offer.py) file is grabs the most recent deal of the day 
from the digitec website and prints the product details, price and URL to stdout.
This output can be forwarded to email or a Telegram-bot.

### Usage

Using [mnemocron/telegram-bot](https://github.com/mnemocron/telegram-bot)
```bash
telegram-bot -u digitecdaily -t "`/home/simon/workspace/digitec-alert/digitec-daily-offer.py`"
```

**Cronjob**

```bash
0 3 * * * telegram-bot -u digitecdaily -t "`/home/simon/workspace/digitec-alert/digitec-daily-offer.py`" --disable-notification > /dev/null 2>&1
```

Sends a silenced message to the username "digitecdaily" at 3 am.

---

## Pricebot 2.0

### Input
The script can take both an input file or a url as an argument.
From the input file, only the lines containing the word 'digitec' or 'galaxus' will be used to look up a price.

```bash
digitecPricebot-2 -o [output directory] -i [input file]
digitecPricebot-2 -o [output directory] -u [url]
```

### Output
The script outputs one `.csv` file for each product specified. The name of the file consists of the article number and a part of the name. For example, this [Samsung SSD](https://www.digitec.ch/de/s1/product/samsung-850-evo-basic-500gb-25-ssd-3481917?tagIds=76) would result in the file name:

```
3481917-Samsung 850 EVO Basic.csv
```

You can specify the output directory with the option `-o [output directory]`

In most cases the bot is used to collect long term changes of the price. Thus, if there already exists a file of a specified product in the output directory, the new price is appended to this file.
If however, the last upodate in the file was made today, the script will not add another line with the same date.
In this case you can force an update using `-t` or `--ignore-time`.

### Running the Bot
#### Examples

testing the script
```bash
digitecPricebot-2 -o ./ -u https://www.digitec.ch/de/s1/product/samsung-850-evo-basic-500gb-25-ssd-3481917?tagIds=76
```

**Cronjob**

```bash
55 0 * * * digitecPricebot-2 -o /var/www/html/digitec/ -i /home/user/Downloads/digitec_url.txt > /dev/null 2>&1
```

cronjob every morning at 0:55am using an input file

### Graphs
The generated files are `TAB`-separated values and can easily be imported into a table calculation program to create fancy graphs.

## License

MIT

   [Digitec Galaxus AG]: <https://www.digitec.ch/en/Wiki/528>
   [Digitec]: <https://www.digitec.ch/en>
   [Galaxus]: <https://www.galaxus.ch/en/>
