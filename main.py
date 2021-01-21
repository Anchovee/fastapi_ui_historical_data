import sqlite3, config, datetime
from fastapi import Request, FastAPI, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import date

import patterns
import alpaca_trade_api as tradeapi
import pandas as pd 
import talib

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    stock_filter = request.query_params.get('filter', False)
    
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # https://youtu.be/fYf3EeupuMo?list=PLvzuUVysUFOuoRna8KhschkVVUo2E2g6G&t=1219
    #function aggregates the select conditions for filter params into one table
    if stock_filter == 'new_closing_highs':
        cursor.execute("""
        SELECT * FROM (
            SELECT symbol, name, stock_id, max(close), date
            FROM stock_price join stock on stock.id = stock_price.stock_id
            GROUP BY stock_id
            ORDER BY symbol
        ) WHERE date = (SELECT max(date) FROM stock_price)
        """)
    elif stock_filter =='new_closing_lows':
        cursor.execute("""
        SELECT * FROM (
            SELECT symbol, name, stock_id, min(close), date
            FROM stock_price join stock on stock.id = stock_price.stock_id
            GROUP BY stock_id
            ORDER BY symbol
        ) WHERE date = (SELECT max(date) FROM stock_price)
        """)#(datetime.datetime.utcnow().date().isoformat(),))
    elif stock_filter =='rsi_overbought':
        cursor.execute("""
            SELECT symbol, name, stock_id, date
            FROM stock_price join stock on stock.id = stock_price.stock_id
            WHERE rsi_14 > 70 and date = (SELECT max(date) FROM stock_price)
            ORDER BY symbol
        """)
    elif stock_filter =='rsi_oversold':
        cursor.execute(""" 
        SELECT symbol, name, stock_id, date
            FROM stock_price join stock on stock.id = stock_price.stock_id
            WHERE rsi_14 < 30 and date = (SELECT max(date) FROM stock_price)
            ORDER BY symbol
        """)    
    elif stock_filter =='below_ma_oversold':
        cursor.execute(""" 
        SELECT symbol, name, stock_id, date
            FROM stock_price join stock on stock.id = stock_price.stock_id
            WHERE rsi_14 < 30 and date = (SELECT max(date) FROM stock_price)
            and close < sma_20 
            ORDER BY symbol
        """)    
    else: 
        cursor.execute("""
            SELECT id, symbol, name FROM stock ORDER BY symbol
            """)
    rows = cursor.fetchall()
    #dictionary db object where you get attributes
    cursor.execute("""
        SELECT symbol, rsi_14, sma_20, sma_50, close
        FROM stock JOIN stock_price ON stock_price.stock_id = stock.id
        WHERE date = (SELECT max(date) FROM stock_price)
    """)
    indicator_rows = cursor.fetchall()
    indicator_values = {}

    for row in indicator_rows:
        indicator_values[row['symbol']] = row
    
    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "indicator_values": indicator_values})

@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * from strategy
    """)

    strategies = cursor.fetchall()

    cursor.execute("""
        SELECT id, symbol, exchange, name FROM stock WHERE symbol = ?
        """, (symbol,))

    row =  cursor.fetchone()
    #row['id'] fetches foreign key linked to db stock table id
    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id = ?
        """, (row['id'],))
    bars = cursor.fetchall()
    
    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": row, "bars": bars, "strategies": strategies}) 

@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO stock_strategy (stock_id,  strategy_id) VALUES (?,?)
    """, (stock_id, strategy_id))
    
    connection.commit()

    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)

@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM strategy
        Where id = ?
    """, (strategy_id,))

    strategy = cursor.fetchone()

    cursor.execute("""
        SELECT symbol, name
        FROM stock JOIN stock_strategy on stock_strategy.stock_id = stock.id
        WHERE strategy_id = ?
    """, (strategy_id,))

    stocks = cursor.fetchall()

    return templates.TemplateResponse("strategy.html", {"request": request, "stocks": stocks, "strategy": strategy})

@app.get("/strategies")
def strategies(request: Request):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * from strategy
    """)

    strategies = cursor.fetchall()
    return templates.TemplateResponse("strategies.html", {'request': request, "strategies":strategies})

@app.get("/orders")
def strategies(request: Request):
    api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)
    orders = api.list_orders(status='all')

    return templates.TemplateResponse("orders.html", {'request': request, 'orders': orders})

@app.get('/candles/{pattern}')
def index(request: Request, pattern):
    pattern = request.query_params.get('pattern', None)##gets the route func value pair and passes pattern string to variable 
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
            
        if pattern:
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
                         
                except:
                    pass
                    
    return templates.TemplateResponse("candles.html", {'patterns': patterns, 'stocks' : stocks, 'current_pattern' : pattern})  