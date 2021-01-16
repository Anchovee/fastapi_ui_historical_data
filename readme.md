## CREATE new DataBase
$ sqlite3 app.db
## Show the database in directory:
sqlite3> .databases
## Create table rows
CREATE TABLE IF NOT EXISTS stock(
   ...> id INTEGER PRIMARY KEY,
   ...> symbol TEXT NOT NULL UNIQUE,
   ...> company TEXT NOT NULL 
   ...> );
## List tables shows table <stock>
sqlite3> .tables
stock
## check db schema
.schema
## Insert
sqlite3> INSERT INTO stock (symbol, company) VALUES ('MSFT', 'Microsoft Inc.')
## show table values with differnt filters:
sqlite3> select * from stock;
sqlite3> select id,symbol from stock;
sqlite3> select id,symbol, company from stock WHERE symbol = 'MSFT';
sqlite3> select id,symbol, company from stock WHERE symbol LIKE 'M%';
sqlite3> select id,symbol, company from stock WHERE symbol LIKE '%Micro%';
sqlite3> select id,symbol, company from stock ORDER BY symbol desc;

## update
sqlite3> UPDATE stock SET company = 'Apple Inc.' WHERE symbol = 'AAPL';
## delete
sqlite3> DELETE from stock WHERE symbol = <symbol>

## cron
press esc.
press i (for "insert") to begin editing the file.
paste the cron command in the file.
press esc again to exit editing mode.
type :wq to save ( w - write) and exit ( q - quit) the file.
The command line utility that can control this is tccutil.

To reset warnings associated with the Terminal app, you can use [tccutil reset All com.apple.Terminal]. This will reset permissions and warnings associated with Terminal back to factory defaults ... but from here you would be allowed to grant permissions to Terminal.

*/1 8-3 * * 1-5 /Users/administrator/db_Trade_app/populate_db.py >> populate.log 2>&1

ls -al //list logs

cat {example}.log}//open log
tail - f {example}.log//monitor las ten logs

## SQL look up stock prices
//** In db browser joining stock id from stock and stock price **//
SELECT symbol, date, open, high, low, close
FROM stock_price
JOIN stock on stock.id = stock_price.stock_id 
WHERE symbol = 'AAPL'
ORDER BY date; //(but main.py function already does this)

## Filtering max close and joining stock_id and stock_price.stock_id
//** In db browser join stock price on,the stock and then join on stock.id equal stockprice.stockid and then we're going to group by stockid so that so when we apply the sql aggregate function we need to get the maximum close of each stock in our database **//

SELECT symbol, name, stock_id, max(close), date
FROM stock_price join stock on stock.id = stock_price.stock_id
GROUP BY stock_id
ORDER BY symbol


## run uvicorn/fastapi
$uvicorn main:app --reload
* fastapi can serve data to react or any other framework

# Get uvicorn request object info
* under index route
print(dir(request))

# Styling
https://semantic-ui.com/introduction/advanced-usage.html
https://semantic-ui.com/collections/table.html

# Check rsi vals in db
select * from stock_price where rsi_14 is not null

# Indicator example of joining table while getting values
# stock_price.stock_id = Foreign key of stock.id
SELECT symbol, rsi_14, sma_20, sma_50, close
FROM stock JOIN stock_price ON stock_price.stock_id = stock.id
WHERE date = '2021-01-14';

