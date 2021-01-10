import sqlite3, config
import alpaca_trade_api as tradeapi
from symbol_list import symbols

connection = sqlite3.connect(config.DB_FILE)

#creates sqlite objects from tuple
connection.row_factory = sqlite3.Row

cursor = connection.cursor()
# cursor.execute("DELETE FROM stock")
cursor.execute("""
    SELECT symbol, name FROM stock
""")

rows = cursor.fetchall()
# ##list comprehension of all symbols in db - checks current db value
# symbols = [row['symbol'] for row in rows]
symbols = symbols

api = tradeapi.REST(config.API_KEY,config.SECRET_KEY, base_url=config.BASE_URL)
assets = api.list_assets()
# later add a list of optionable stocks from tweets if asset.symbol in {optionable_list} execute
for asset in assets:
    try:
        if asset.symbol in symbols and asset.status == 'active':
            print(f'Added a new stock {asset.symbol} {asset.name}')
            cursor.execute("INSERT INTO stock (symbol, name) VALUES (?, ?)", (asset.symbol, asset.name))
    except Exception as e:
        print(asset.symbol, e)
connection.commit()
