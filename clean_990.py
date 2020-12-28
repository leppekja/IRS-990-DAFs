import xml.etree.ElementTree as et
import requests
import read_xmls  
import pandas as pd
import numpy as np  
import argparse
import re
import read_990 as rd

def clean_daf_grantee_data(daf_dataframe, daf_sponsor_ein, daf_sponsor_taxyear):
    '''
    Adds the sponsoring organization EIN to each grant and converts
    grant amounts to floats. 
    Joins Address lines together and checks for any names c/o names in the address
    that should be redacted
    Note that daf_dataframe may, for some 990s, be None. 
    '''
    # details for sponsoring orgs included in different dataframe
    if daf_dataframe is not None:
        # Get rid of null lines parsed from the Schedule I
        # May be a way to do this more efficiently while parsing?
        try:
            daf_dataframe['BusinessNameLine1Txt'].replace('', np.nan, inplace=True)
            daf_dataframe.dropna(subset=['BusinessNameLine1Txt'], inplace=True)
        except KeyError:
            # May be that an organization provided a grant to an individual
            # seen in 990 form as GrantsOtherAsstToIndivInUSGrp
            # Example Form: https://s3.amazonaws.com/irs-form-990/201800089349300610_public.xml
            pass
        # add name of DAF sponsoring organization into grantee data
        daf_dataframe['Sponsor'] = daf_sponsor_ein
        daf_dataframe['TAXYEAR'] = daf_sponsor_taxyear

        # check for any C/O names in the address field
        if 'AddressLine1Txt' in daf_dataframe.columns:
            in_care_of = re.compile("c/o", flags=re.IGNORECASE)
            # And get rid of them (don't want to share individual names)
            daf_dataframe['AddressLine1Txt'].replace(in_care_of, '', inplace=True, regex=True)
        
        # join address lines together
        if 'AddressLine2Txt' in daf_dataframe.columns:
            daf_dataframe['Address'] = daf_dataframe['AddressLine1Txt'] + daf_dataframe['AddressLine2Txt']
        else:
            pass
        try:
            daf_dataframe['CashGrantAmt'] = daf_dataframe.CashGrantAmt.astype(float)
        except AttributeError:
            # Organization may not have put amounts
            pass

        return daf_dataframe
    else: 
        print(daf_sponsor_ein, "had no grants?")
        return None
