import psycopg2
import argparse
import pandas as pd

database_col_names = [
        'sponsor_ein',
        'name',
        'address_line_1',
        'city',
        'state',
        'zip_code',
        'latitude',
        'longitude',
        'daf_held_cnt',
        'daf_contri_amt',
        'daf_grants_amt', 
        'daf_eoy_amt',
        'disclosed_legal',
        'disclosed_prps',
        'other_act_held_cnt',
        'other_act_contri_amt',
        'other_act_grants_amt',
        'other_act_eoy_amt']

database_grantee_col_names = ['grantee_ein',
                            'name',
                            'address_line_1',
                            'city',
                            'state',
                            'zip_code', 
                            'latitude',
                            'longitude',
                            'irs_section_desc']


def update_sponsor_csv(file_path, suffix, drop_duplicates=True):
    '''
    Data cleaning steps for uploading a batch testing csv
    to the database.
    '''
    data = pd.read_csv(file_path)
    try:
        del data['Unnamed: 0']
    except KeyError:
        pass
    if 'latitude' not in data.columns:
        data.insert(6, 'latitude', 0)
    if 'longitude' not in data.columns:
        data.insert(7, 'longitude', 0)
    
    data.columns = database_col_names

    data['zip_code'] = data['zip_code'].astype(str).str[:5]
    # Some organizations filed twice in one year, so if testing,
    # can just drop these organizations 
    if drop_duplicates:
        data.drop_duplicates(subset='sponsor_ein', inplace=True)
    
    if data.isna().any().any():
        data.fillna(0, inplace=True)
    for col in data.select_dtypes(include='float64').columns.values:
        if (col != 'latitude') and (col != 'longtitude'):
            data[col] = data[col].astype('int64')
    data.to_csv('Sponsors' + suffix + '.csv', index=False)
    return None

def update_grantee_csv(file_path, suffix, drop_duplicates=True):
    '''
    Data cleaning steps for uploading a batch testing csv
    to the database.
    '''   
    data = pd.read_csv(file_path)
    try:
        del data['Unnamed: 0']
    except KeyError:
        pass

    data = data.loc[:, ['BusinessNameLine1Txt','AddressLine1Txt',
                        'CityNm','StateAbbreviationCd',
                        'ZIPCd','RecipientEIN','IRCSectionDesc']]
    
    data.insert(0, 'grantee_ein', data['RecipientEIN'])
    data.insert(6,'latitude', 0)
    data.insert(7,'longitude',0)
    del data['RecipientEIN']

    data.columns = database_grantee_col_names

    data['zip_code'] = data['zip_code'].astype(str).str[:5]

    if data.isna().any().any():
        data.fillna(0, inplace=True)

    for col in data.select_dtypes(include='float64').columns.values:
        data[col] = data[col].astype('int64')

    data.drop_duplicates(subset='grantee_ein', inplace=True)
    data.to_csv('Grantees' + suffix + '.csv', index=False)

def csv_load(file_path, table_name, host, port, user_name, db_name, password):
    '''
    Load data from csv file into database tables for testing.
    Input:
    file: csv file
    table_name: which table to input data into. Either 'sponsors' or 'grantees'.
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
        try:
            cur.copy_expert(copy, f)
        except Exception as e:
            print(e)
            conn.rollback()

        # if table_name.lower() == 'grantees':
        #     copy_grantee = """COPY Grantee
        #             FROM STDIN
        #             WITH (FORMAT csv, HEADER TRUE);"""
        #     self.cur.copy_expert(copy, f)

            conn.commit()
    
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