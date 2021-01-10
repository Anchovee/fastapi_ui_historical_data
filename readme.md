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

*/1 * * * * /Users/administrator/db_Trade_app/populate_db.py >> populate.log 2>&1

ls -al //check log
cat -populate.log

## SQL look up stock prices
## Joining stock id from stock and stock price
SELECT symbol, date, open, high, low, close
FROM stock_price
JOIN stock on stock.id = stock_price.stock_id 
WHERE symbol = 'AAPL'
ORDER BY date;