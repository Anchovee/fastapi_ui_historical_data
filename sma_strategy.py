import sqlite3, config
import alpaca_trade_api as tradeapi
import pandas as pd 

from datetime import date
from alphaVantageAPI.alphavantage import AlphaVantage ##pip install alphaVantage-api##

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

#access the id from strategy table to reference 
cursor.execute("""
    SELECT id FROM strategy WHERE name == 'opening_range_breakout'
""")
#store the id from the accessed db row object  
strategy_id = cursor.fetchone()['id']

 ##scan barsets of stock_prices table for strategy criteria

##join TABLE stock symbols, names with the TABLE stock_strategy
##where the stock_strategy id contains stock.id 
cursor.execute("""
    SELECT symbol, name FROM stock
    JOIN stock_strategy on stock_strategy.stock_id = stock.id 
    WHERE stock_strategy.strategy_id = ?
    """,(strategy_id,))

#store db objects
stocks = cursor.fetchall()
#get row cell w/ table['column'] index
symbols = [stock['symbol'] for stock in stocks]
