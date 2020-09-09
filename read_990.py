import xml.etree.ElementTree as et
import requests
import read_xmls  
import pandas as pd
import numpy as np  
import argparse
import re

'''
FIELDS OBTAINED
returnVersion
ReturnHeader / ReturnTypeCd
ReturnData / IRS990 / DonorAdvisedFundInd
EIN
BusinessNameLine1Txt
All fields in: 
.//Filer/USAddress
ReturnData / IRS990ScheduleI
ReturnData / IRS990ScheduleD
'''
# See models.py for primary source. Additional id col created in tables
# need to figure out pipeline into django better
# these are only for testing in summer 2020

SPONSOR_COLUMN_NAMES = [
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

GRANTEE_COLUMN_NAMES = ['grantee_ein',
                        'name',
                        'address_line_1',
                        'city',
                        'state',
                        'zip_code',
                        'latitude',
                        'longitude',
                        'irs_section_desc']

DONATION_COLUMN_NAMES = ['grantee_ein',
                        'sponsor_ein',
                        'cash_grant_amt',
                        'purpose_of_grant',
                        'grant_type']

def read_form(document=None, download=True):
    '''
    Reads in IRS 990 form from download or link, if download True.
    Input: link or file name, boolean for download
    Output: Element object
    '''
    #Get data and transform to tree object
    if download:
        r = requests.get(document)
        root = et.fromstring(r.content)
    else:
        tree = et.parse(document)
        root = tree.getroot()

    #remove namespace prefixes
    read_xmls.clean_xml(root)

    return root

def get_form_version(tree):
    '''
    Checks IRS Form 990 version
    Input: tree
    Output: Form number
    '''
    return tree.attrib['returnVersion']

def get_form_type(tree):
    '''
    Check form type 
    Input: tree
    Output: Form type
    '''
    return tree.find('ReturnHeader').find('ReturnTypeCd').text

def confirm_daf_fund(tree):
    '''
    Checks IRS Form 990 Part IV line 6 if yes.
    Input: tree
    Output: Boolean
    '''
    # Does this change based on form type or version?
    if tree.find('ReturnData').find('IRS990').find('DonorAdvisedFundInd').text == str(1):
        return True
    else:
        return False

def get_form_headers(tree):
    '''
    Returns a dictionary with organization EIN,
    name, US address, Tax Year, and Tax Period Beginning and End from a 990 form.
    '''
    # obtain data from tree
    data = {}
    data['EIN'] = read_xmls.search_tree(tree, 'EIN')['EIN']
    # Name may have multiple lines
    name_fields = read_xmls.search_tree(tree, 'BusinessName', True)
    data['NAME'] = ' '.join(name_fields.values())
    
    data['TAXYEAR'] = read_xmls.search_tree(tree, 'TaxYr')['TaxYr']
    data['TAXYRSTART'] = read_xmls.search_tree(tree, 'TaxPeriodBeginDt')['TaxPeriodBeginDt']
    data['TAXYREND'] = read_xmls.search_tree(tree, 'TaxPeriodEndDt')['TaxPeriodEndDt']

    for child in tree.find(".//Filer/USAddress"):
        data[child.tag] = child.text

    return data

def get_summary_data(tree):
    '''
    Collects the summary data from Part I of the 
    written form, as it may differ from other parts.
    Obtains (ACTIVITIES AND GOVERNENCE)number of 
    individuals employed, number of volunteers; 
    (REVENUE) total contributions and grants, program
    service revenue, investment income, other revenue,
     and total revenue; (EXPENSES) grants and similar
     amounts paid, salaries, other compensation.
    '''
    # probably should add something here at some point
    # low priority, though, see Open990.org for this data
    return None

def get_schedule_i(root):
    '''
    Iterates through all grantees listed in a 990
    Schedule I form and returns a dataframe with 
    their information.
    Input: Element object
    Output: Pandas Dataframe
    '''
    if read_xmls.search_tags(root, 'ScheduleI'):
        grantees = []
        for child in root.find('ReturnData').find('IRS990ScheduleI'):
            org = {}
            if (child.tag == 'RecipientTable') or (child.tag == 'GrantsOtherAsstToIndivInUSGrp'):
                for item in child:
                # Get only grantee information, not Supplemental Information
                    if item:
                        for subitem in item:
                            org[subitem.tag] = subitem.text
                    else:
                        org[item.tag] = item.text
            else:
                pass
            grantees.append(org)
    else:
        return None
    return pd.DataFrame(grantees)

def get_schedule_d(root):
    '''
    Collects data from Schedule D pertaining to 
    donor-advised funds: number of funds, value
    of contributions to, value of grants from,
    value at end of year, and if all donors were
    notified of their rights to their donation.
    Input: Element Object
    Output: Dictionary
    '''
    if read_xmls.search_tags(root, 'ScheduleD'):
        tags = ['DonorAdvisedFundsHeldCnt', 'DonorAdvisedFundsContriAmt', 'DonorAdvisedFundsGrantsAmt',
                'DonorAdvisedFundsVlEOYAmt', 'DisclosedOrgLegCtrlInd', 'DisclosedForCharitablePrpsInd',
                'FundsAndOtherAccountsHeldCnt','FundsAndOtherAccountsContriAmt',
                'FundsAndOtherAccountsGrantsAmt','FundsAndOtherAccountsVlEOYAmt']
        info = {}
        
        for tag in tags:
            child = root.find('ReturnData').find('IRS990ScheduleD').find(tag)
            try:
                # Catch any missing field and move on
                if child.text:
                    info[child.tag] = child.text
            except AttributeError:
                pass 

        return info

    else:
        return None

    return info

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
        in_care_of = re.compile("c/o", flags=re.IGNORECASE)
        # And get rid of them (don't want to share individual names)
        daf_dataframe['AddressLine1Txt'].replace(in_care_of, '', inplace=True, regex=True)
        
        # join address lines together
        try:
            daf_dataframe['Address'] = daf_dataframe['AddressLine1Txt'] + daf_dataframe['AddressLine2Txt']
        except Error as e:
            print(e)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Read a IRS 990 Form and download data \
                        associated with a donor-advised fund')
    parser.add_argument('-form',type=str,
                    help='link or file name to XML format 990 form')
    parser.add_argument('--download', action="store_true",
                    help="whether to download the form from online (True, default) \
                        or access it locally")
    parser.add_argument('--verbose', action="store_true",
                    help="whether to print progress")
    args = parser.parse_args()

    #read in document
    tree = read_form(document=args.form, download=args.download)
    #confirm DAF
    if confirm_daf_fund(tree):
        if args.verbose:
            print("DAF Confirmed. Getting data...")
        #get org headers
        sponsor = get_form_headers(tree)
        #get schedule D
        daf_details = get_schedule_d(tree)
        #combine headers and schedule D
        sponsor_details = pd.DataFrame([sponsor, daf_details])
        #get schedule I
        grantees = get_schedule_i(tree)
        #clean schedule I
        if grantees is not None:
            grantees = clean_daf_grantee_data(grantees, sponsor['EIN']) 
        #save dataframes with org info and grantees (I)
            grantees.to_csv(sponsor['NAME'] + "_Grantees.csv")
        sponsor_details.to_csv(sponsor['NAME'] + "_Details.csv")
        if args.verbose:
            print("Documents saved!")
    else:
        if args.verbose:
            print("No DAF found.")

