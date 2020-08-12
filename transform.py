'''
Functions for step 2 of ETL
#################################
Completes any data cleaning steps not solved during XML parsing
and readies data for csv export or database bulk upload
'''
sponsor_col_names = [
        'sponsor_ein',
        'name',
        'address_line_1',
        'city',
        'state',
        'zip_code',
        'latitude',
        'longitude']


worth_col_names = [
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

database_donation_col_names = [ 'cash_grant_amt',
                                'purpose_of_grant',
                                'grant_type',
                                'grantee_ein',
                                'sponsor_ein']

def update_sponsor_csv(file_path, suffix, drop_duplicates=True):
    '''
    Data cleaning steps for uploading a batch testing csv
    to the database.
    '''
    data = pd.read_csv(file_path)
    try:
        # If data was saved to csv without index=False option
        del data['Unnamed: 0']
    except KeyError:
        pass

    # Holdouts for geocoding
    # may just end up using zip code with google maps/open street map API?
    if 'latitude' not in data.columns:
        data.insert(6, 'latitude', 0)
    if 'longitude' not in data.columns:
        data.insert(7, 'longitude', 0)

    # Copy from for bulk upload; the names need to match and be in the correct order
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

    data['zip_code'] = data['zip_code'].astype(str).str[:5].astype('int64')
    data['irs_section_desc'] = data['irs_section_desc'].str[:10]

    if data.isna().any().any():
        data.fillna(0, inplace=True)

    for col in data.select_dtypes(include='float64').columns.values:
        data[col] = data[col].astype('int64')

    data.drop_duplicates(subset='grantee_ein', inplace=True)
    data.to_csv('Grantees' + suffix + '.csv', index=False)

    return None

def update_donation_csv(file_path, suffix, drop_duplicates=True):
    data = pd.read_csv(file_path)

    data = data.loc[:, ['CashGrantAmt', 'PurposeOfGrantTxt','GrantTypeTxt','RecipientEIN', 'Sponsor']]
    data.columns = database_donation_col_names
    data['purpose_of_grant'] = data['purpose_of_grant'].str[:100]
    data['grant_type'] = data['grant_type'].str[:50]

    data.dropna(subset=['grantee_ein'], inplace=True)
    # Need to change this - grant type is frequently null
    if data.isna().any().any():
        data.fillna(0, inplace=True)

    for col in data.select_dtypes(include='float64').columns.values:
        data[col] = data[col].astype('int64')
    data.index.name = 'id'

    data.to_csv('Donations' + suffix + '.csv', index=True)
    return None