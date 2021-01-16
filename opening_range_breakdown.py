import sqlite3, config, datetime
import alpaca_trade_api as tradeapi
import pandas as pd 

from datetime import date
from alphaVantageAPI.alphavantage import AlphaVantage ##pip install alphaVantage-api##
import notifications

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

#access the id from strategy table to reference 
cursor.execute("""
    SELECT id FROM strategy WHERE name == 'opening_range_breakdown'
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

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)

current_date = datetime.datetime.utcnow().date()
###alpaca orders
###debug algo
#orders = api.list_orders(status='all', limit=300, after=f'{current_date}T1:30:00Z')
orders = api.list_orders()
existing_order_symbols = [order.symbol for order in orders]

# start_minute_bar = f'{current_date} 09:30-04:00' 
# end_minute_bar = f'{current_date} 09:45-04:00'
NY = 'America/New_York'
start=pd.Timestamp('2021-01-06 9:30', tz=NY).isoformat()
end=pd.Timestamp('2021-01-06 9:45', tz=NY).isoformat()

# current_date = '2021-01-05' #date.datetime.utcnow().date()
# start_minute_bar = f'{current_date} 09:30-04:00' 
# end_minute_bar = f'{current_date} 09:45-04:00'
start_date=pd.Timestamp('2021-01-06 9:30', tz=NY).isoformat()
end_date=pd.Timestamp('2021-01-06 16:00', tz=NY).isoformat()
messages = []
for symbol in symbols:
    # minute_bars = api.polygon.historic_agg_v2(symbol, 15, 'minute', _from='2021-01-05', to='2021-01-05')
    minute_bars = api.get_barset(symbol, '5Min', start=start_date, end=end_date).df

    opening_range_mask = (minute_bars.index >= start) & (minute_bars.index < end)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    
    opening_range_low = opening_range_bars[symbol]['low'].min()
    opening_range_high = opening_range_bars[symbol]['high'].max()
    opening_range = opening_range_high - opening_range_low
    print(symbol, opening_range_low, opening_range_high)
    #find 1st min bar wtih close above opening range high
    after_opening_range_mask = minute_bars.index >= end
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]
    
    after_opening_range_breakdown = after_opening_range_bars[after_opening_range_bars[symbol]['close'] < opening_range_low]
   
    if not after_opening_range_breakdown.empty:
        '''alpaca trade check for existing orders (line 37)'''
        #if symbol not in existing_orders_symbols 
        limit_price = after_opening_range_breakdown.iloc[0][symbol]['close']
        print("limit: ", limit_price)
        # print(f'placing order for{symbol} at {limit_price}, closed above {opening_range_low} at {after_opening_range_breakdown.iloc[0]}')
        messages.append(f'Subject: ORBD strategy pew pew\n\nplacing order for{symbol} at {limit_price}, closed below {opening_range_low}\n\n{after_opening_range_breakdown.iloc[0]}\n\n')
        #https://youtu.be/RZ_4OI_K6Aw?list=PLvzuUVysUFOuoRna8KhschkVVUo2E2g6G&t=1772
        ###alpaca api order
        try:
            api.submit_order(
                symbol=symbol,
                side='sell',
                type='limit',
                qty='100',
                time_in_force='day',
                order_class='bracket',
                limit_price= limit_price,
                take_profit=dict(
                    limit_price = round(limit_price, 2) + round(opening_range, 2)+ .01,
                ),
                stop_loss=dict(
                    stop_price=round(limit_price, 2) - round(opening_range, 2)-.01,
                )
            )
            print('prices:', round(limit_price, 2) + round(opening_range, 2))
            print('prices:', round(limit_price, 2) - round(opening_range, 2))
            ''' cron job
            */1 * * * * /Users/administrator/db_Trade_app/venv/bin/python/opening_range_breakdown.py >> trade.log 2>&1
            '''
            print(messages)
            notifications.email(messages)
        except Exception as e:
            print(f'Error submiting {e}')
        else:
            print(f'Order exists for {symbol}, skipped')
