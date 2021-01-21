import sqlite3, config, csv, talib

from pandas import DataFrame
import pandas as pd

# pattern = request.query_params.get('pattern', None)##gets the route func value pair and passes pattern string to variable 
pattern = 'CDLDOJI'#'CDL3INSIDE'
#dictionary symbol and bullish/bearish-signal

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

stocks = []
stock_ids = {}
with open('qqq.csv') as f:
    for row in csv.reader(f):
        stocks += [row[1]]

cursor.execute("""
    SELECT * from stock
""")

symbols = cursor.fetchall()

## loop through database object
for symbol in symbols:
    if symbol['symbol'] in stocks:
        ##assign stock name to key value
        db_symbol = symbol['symbol']
        ##append key value and assign value value
        stock_ids[db_symbol] = symbol['id']

# loop through stock_id dictionary
for stock_row in stock_ids:
    current_id = stock_ids[stock_row]
    df = pd.read_sql_query(f'SELECT date, stock_id, open, high, low, close FROM stock_price WHERE stock_id == {current_id}', connection) 
    # print (stock_row, '\n', df)
    cursor.execute(f'SELECT date, stock_id, open, high, low, close FROM stock_price WHERE stock_id == {current_id}')
    # prices = cursor.fetchall()
    # for df in prices:
        
    if pattern:
        # datafiles = os.listdir('datasets/daily') ##get the directory of stock data
        # for filename in datafiles:
        #     df = pd.read_csv('datasets/daily/{}'.format(filename))
        pattern_function = getattr(talib, pattern) #on talib all the functions are named attributes, pass name of function into a variable to call the function
        try:
            result = pattern_function(df['open'], df['high'], df['low'], df['close'])
           
       last = result.tail(1).values ##get's the last pattern I believe
                #print (last)

                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
                    #print("{} triggered {}".format(filename, pattern)) 
            except:
                pass
                   
    return render_template("candles.html", patterns=patterns, stocks = stocks, current_pattern = pattern)