import os
import sys
# import time
import pandas as pd
import numpy as np
# from sqlalchemy import create_engine
import threading
# from timeit import default_timer as timer

os.path.dirname(os.path.abspath(__file__))

def clean_df_db_dups(df, tablename, engine, dup_cols=[], 
                         filter_continuous_col=None, filter_categorical_col=None):
    """
    Remove rows from a dataframe that already exist in a database
    Required:
        df : dataframe to remove duplicate rows from
        engine: SQLAlchemy engine object
        tablename: tablename to check duplicates in
        dup_cols: list or tuple of column names to check for duplicate row values
    Optional:
        filter_continuous_col: the name of the continuous data column for BETWEEEN min/max filter
                               can be either a datetime, int, or float data type
                               useful for restricting the database table size to check
        filter_categorical_col : the name of the categorical data column for Where = value check
                                 Creates an "IN ()" check on the unique values in this column
    Returns
        Unique list of values from dataframe compared to database table
    """
    args = 'SELECT %s FROM %s' %(', '.join(['"{0}"'.format(col) for col in dup_cols]), tablename)
    args_contin_filter, args_cat_filter = None, None
    if filter_continuous_col is not None:
        if df[filter_continuous_col].dtype == 'datetime64[ns]':
            args_contin_filter = """ "%s" BETWEEN Convert(datetime, '%s') 
                                          AND Convert(datetime, '%s')""" %(filter_continuous_col, 
                              df[filter_continuous_col].min(), df[filter_continuous_col].max())

    
    if filter_categorical_col is not None:
        args_cat_filter = ' "%s" in(%s)' %(filter_categorical_col, 
                          ', '.join(["'{0}'".format(value) for value in df[filter_categorical_col].unique()]))

    if args_contin_filter and args_cat_filter:
        args += ' Where ' + args_contin_filter + ' AND' + args_cat_filter
    elif args_contin_filter:
        args += ' Where ' + args_contin_filter
    elif args_cat_filter:
        args += ' Where ' + args_cat_filter

    df.drop_duplicates(dup_cols, keep='last', inplace=True)
    df = pd.merge(df, pd.read_sql(args, engine), how='left', on=dup_cols, indicator=True)
    df = df[df['_merge'] == 'left_only']
    df.drop(['_merge'], axis=1, inplace=True)
    return df

def to_sql_newrows(df, pool_size, *args, **kargs):
    """
    Extend the Python pandas to_sql() method to thread database insertion

    Required: 
        df : pandas dataframe to insert new rows into a database table
        POOL_SIZE : your sqlalchemy max connection pool size.  Set < your db connection limit.
                    Example where this matters: your cloud DB has a connection limit.
    *args:
        Pandas to_sql() arguments.  

        Required arguments are:
            tablename : Database table name to write results to
            engine : SqlAlchemy engine

        Optional arguments are:
            'if_exists' : 'append' or 'replace'.  If table already exists, use append.
            'index' : True or False.  True if you want to write index values to the db.


    Credits for intial threading code:
        http://techyoubaji.blogspot.com/2015/10/speed-up-pandas-tosql-with.html
    """

    CHUNKSIZE = 1000
    INITIAL_CHUNK = 100
    if len(df) > CHUNKSIZE:
        #write the initial chunk to the database if df is bigger than chunksize
        df.iloc[:INITIAL_CHUNK, :].to_sql(*args, **kargs)
    else:
        #if df is smaller than chunksize, just write it to the db now
        df.to_sql(*args, **kargs)

    workers, i = [], 0

    for i in range((df.shape[0] - INITIAL_CHUNK)/CHUNKSIZE):
        t = threading.Thread(target=lambda: df.iloc[INITIAL_CHUNK+i*CHUNKSIZE:INITIAL_CHUNK+(i+1)*CHUNKSIZE].to_sql(*args, **kargs))
        t.start()
        workers.append(t)
        
    df.iloc[INITIAL_CHUNK+(i+1)*CHUNKSIZE:, :].to_sql(*args, **kargs)
    [t.join() for t in workers]

