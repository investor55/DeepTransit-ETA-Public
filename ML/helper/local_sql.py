import sqlite3
import pandas as pd

pd.set_option('display.max_columns', None)

def read_db(db_path, query):
    """
    Reads a local database using pandas.

    Parameters:
    db_path (str): The path to the SQLite database file.
    query (str): The SQL query to execute.

    Returns:
    pd.DataFrame: The resulting dataframe after executing the query.
    """
    # Establish a connection to the SQLite database
    conn = sqlite3.connect(db_path)

    try:
        # Use pandas to execute the SQL query and read the result into a DataFrame
        df = pd.read_sql(query, conn)
    finally:
        # Close the connection
        conn.close()

    return df