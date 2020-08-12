import psycopg2
import argparse
import pandas as pd

def csv_load(file_path, table_name, host, port, user_name, db_name, password):
    '''
    Load data from csv file into database tables for testing.
    ***SPONSORS MUST BE LOADED IN BEFORE GRANTEES***
    Input:
    file: csv file
    table_name: which table to input data into. Either 'sponsors' or 'grantees'.
    if sponsors, will update taxperiod table as well
    if grantees, will update donation table as well
    host: database host
    port: port connection is listening on
    db_name: database name
    user_name: username for db
    password: password for db
    Output: None
    '''
    conn = psycopg2.connect(dbname=db_name, user=user_name, password=password,
                            host=host, port=port)
    cur = conn.cursor()

    with open(file_path) as f:
        if table_name.lower() == 'sponsors':
            copy = """COPY dafs_sponsor
                  FROM STDIN
                  WITH (FORMAT csv, HEADER TRUE);"""
        elif table_name.lower() == 'grantees':
            copy = """COPY dafs_grantee
                  FROM STDIN
                  WITH (FORMAT csv, HEADER TRUE);""" 
        elif table_name.lower() == 'donations':
             copy = """COPY dafs_donation
                  FROM STDIN
                  WITH (FORMAT csv, HEADER TRUE);""" 
        else:
            print("Check the table name!")
                                        
        try:
            cur.copy_expert(copy, f)
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Read a IRS 990 Form and download data \
                        associated with a donor-advised fund')
    parser.add_argument('-file_path',type=str,
                    help='link or file name to XML format 990 form')
    parser.add_argument('-table_name',type=str,
                    help='link or file name to XML format 990 form')
    parser.add_argument('-host', type=str,
                    help="whether to download the form from online (True, default) \
                        or access it locally")
    parser.add_argument('-port', type=int,
                    help="whether to print progress")    
    parser.add_argument('-username',type=str,
                    help='link or file name to XML format 990 form')
    parser.add_argument('-dbname',type=str,
                    help='link or file name to XML format 990 form')
    parser.add_argument('-password',type=str,
                    help='link or file name to XML format 990 form')                                       
    args = parser.parse_args()
    csv_load(file_path=args.file_path, table_name=args.table_name, host=args.host, 
            port=args.port, user_name=args.username, db_name=args.dbname, password=args.password)