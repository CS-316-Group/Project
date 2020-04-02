import csv
from io import StringIO
import pandas as pd 


def copy_df_to_db(df, table_name, conn, cursor):
    """
    Given pandas dataframe, raw database connection, and cursor, 
    performs builk insert into database 
    """
    output = StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    # null values become ''
    cursor.copy_from(output, table_name, null="")
    conn.commit()


