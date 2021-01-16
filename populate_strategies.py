import sqlite3, config

connection = sqlite3.connect(config.DB_FILE)
cursor = connection.cursor()

strategies = ['opening_range_breakout', 'opening_range_breakdown', 'sma_avgerage_range']

for strategy in strategies:
    cursor.execute("""
        INSERT INTO strategy (name) VALUES (?)
    """, (strategy,))

# cursor.execute("""
#     DELETE FROM strategy
# """)

connection.commit()