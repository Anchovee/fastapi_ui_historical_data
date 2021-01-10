import sqlite3, config
from fastapi import Request
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):

    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

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
        SELECT id, symbol, name FROM stock WHERE symbol = ?
        """, (symbol,))

    row =  cursor.fetchone()
    #row['id'] fetches foreign key linked to db stock table id
    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id = ?
        """, (row['id'],))
    bars = cursor.fetchall()
    
    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": row, "bars": bars}) 