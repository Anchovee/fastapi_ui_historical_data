import sqlite3, config, datetime
from fastapi import Request, FastAPI, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

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
        ) WHERE date = ?
        """, ('2021-01-05',))#(datetime.datetime.utcnow().date().isoformat(),))
    else: 
        cursor.execute("""
            SELECT id, symbol, name FROM stock ORDER BY symbol
            """)
    #dictionary db object where you get attributes
    rows = cursor.fetchall()
    
    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows})

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
        SELECT id, symbol, exchange name FROM stock WHERE symbol = ?
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