import config, sqlite3 
import alpaca_trade_api as trade_api 

connection = sqlite3.connect(config.DB_FILE)

connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id, symbol, name FROM stock
    """)

rows = cursor.fetchall()
symbols = [row['symbol'] for row in rows]

stock_dict = {}
for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']

api = trade_api.REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)

chunk_size = 200 
for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]
    barsets = api.get_barset(symbol_chunk, 'day')

    # loop over keys in barset dictionary
    for symbol in barsets:
        print(f'processing {symbol}')
        #loop over bar value in dictionary
        for bar in barsets[symbol]:
            stock_id = stock_dict[symbol]
            cursor.execute("""
                INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
                VALUES (?,?,?,?,?,?,?)
            """, (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v))
            

# #polygon integration requires alpaca upgrade or direct access through polygon api
# minute_bars = api.polygon.historic_agg_v2('Z', 1, 'minute', _from='2020-10-02', to= '2020-10-22')
# for bar in minute_bars:
#     print(bar)

connection.commit()