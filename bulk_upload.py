import psycopg2
import argparse
import pandas as pd

def csv_load(sponsors_file, grantees_file,
            taxperiod_file, worth_file,
            donations_file, host, port, 
            user_name, db_name, password):
    '''
    Load data from csv file into database tables for testing.
    ***SPONSORS MUST BE LOADED IN BEFORE GRANTEES***
    Input:
    files: csv files for sponsor, grantee, taxperiod, 
            donation, and worth tables
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

    upload_files = [('sponsors', sponsors_file),
                    ('taxperiod', taxperiod_file),
                    ('grantees', grantees_file),
                    ('worth', worth_file),
                    ('donations', donations_file)]

    copy_statements = {'sponsors':
            """COPY dafs_sponsor
            FROM STDIN
            WITH (FORMAT csv, HEADER TRUE);""",
            'taxperiod':
            """COPY dafs_taxperiod
            FROM STDIN
            WITH (FORMAT csv, HEADER TRUE);""",     
            'grantees':       
            """COPY dafs_grantee
            FROM STDIN
            WITH (FORMAT csv, HEADER TRUE);""",
            'worth':
            """COPY dafs_worth
            FROM STDIN
            WITH (FORMAT csv, HEADER TRUE);""",
            'donations':
            """COPY dafs_donation
            FROM STDIN
            WITH (FORMAT csv, HEADER TRUE);""" }
    
    for item in upload_files:
        name, table = item
        with open(table) as f:
            try:
                cur.copy_expert(copy_statements[name], f)
                conn.commit()
            except Exception as e:
                print(e)
                conn.rollback()
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='bulk upload data files to database')
    parser.add_argument('-sponsor',type=str,
                    help='sponsor table csv')
    parser.add_argument('-grantee',type=str,
                    help='grantee table csv')
    parser.add_argument('-tax',type=str,
                    help='tax table csv')
    parser.add_argument('-worth',type=str,
                    help='worth table csv')
    parser.add_argument('-donation',type=str,
                    help='donation table csv')
    parser.add_argument('-host', type=str,
                    help="db host")
    parser.add_argument('-port', type=int,
                    help="db port")    
    parser.add_argument('-username',type=str,
                    help='db username')
    parser.add_argument('-dbname',type=str,
                    help='db name')
    parser.add_argument('-password',type=str,
                    help='db password')                                       
    args = parser.parse_args()
    csv_load(sponsors_file=args.sponsor, grantees_file=args.grantee,
            taxperiod_file=args.tax, worth_file=args.worth,
            donations_file=args.donation, host=args.host, 
            port=args.port, user_name=args.username, db_name=args.dbname, password=args.password)