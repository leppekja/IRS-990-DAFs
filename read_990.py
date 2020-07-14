import xml.etree.ElementTree as et
import requests
import read_xmls  
import pandas as pd  
import argparse

parser = argparse.ArgumentParser(
            description='Read a IRS 990 Form and download data \
                        associated with a donor-advised fund')
parser.add_argument('-form',type=str,
                    help='link or file name to XML format 990 form')
parser.add_argument('-download', type=bool, default=True,
                    help="whether to download the form from online (True, default) \
                        or access it locally")
args = parser.parse_args()


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

def confirm_daf_fund(tree):
    '''
    Checks IRS Form 990 Part IV line 6 if yes.
    Input: tree
    Output: Boolean
    '''
    if tree.find('ReturnData').find('IRS990').find('DonorAdvisedFundInd').text == str(1):
        return True
    else:
        return False

def get_form_headers(tree):
    '''
    Returns a dictionary with organization EIN,
    name, and US address from a 990 form.
    '''
    #obtain data from tree
    data = {}
    data['EIN'] = read_xmls.search_tree(tree, 'EIN')['EIN']
    data['NAME'] = read_xmls.search_tree(tree, 'BusinessName', True)['BusinessNameLine1Txt']
    for child in tree.find(".//Filer/USAddress"):
        data[child.tag] = child.text

    return data

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
            for item in child:
                if item:
                    for subitem in item:
                        org[subitem.tag] = subitem.text
                else:
                    org[item.tag] = item.text
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
        info = {}
        count = 0
        for child in root.find('ReturnData').find('IRS990ScheduleD'):
            if count == 6:
                break
            else:
                info[child.tag] = child.text
                count += 1

        return info

    else:
        return None

    return info

def clean_daf_grantee_data(daf_dataframe, daf_sponsor):
    # add name of DAF sponsoring organization
    # details for sponsoring orgs included in different dataframe
    daf_dataframe['Sponsor'] = daf_sponsor

    daf_dataframe['CashGrantAmt'] = daf_dataframe.CashGrantAmt.astype(float)

    return daf_dataframe

if __name__ == "__main__":
    #read in document
    tree = read_form(document=args.form, download=args.download)
    #confirm DAF
    if confirm_daf_fund(tree):
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
        grantees = clean_daf_grantee_data(grantees, sponsor['NAME']) 
        #save dataframes with org info and grantees (I)
        grantees.to_csv(sponsor['NAME'] + "_Grantees")
        sponsor_details.to_csv(sponsor['NAME'] + "_Details")
        print("Documents saved!")
    else:
        print("No DAF found.")

