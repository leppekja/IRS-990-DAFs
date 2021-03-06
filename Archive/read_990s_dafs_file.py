import requests
import read_990 as rd 
import pandas as pd 
import argparse
import os
import time


def get_data(file_or_folder, start, end, verbose=False):
    '''
    Read AWS index file or folder of forms and aggregate Schedule I
    and sponsoring organization forms.
    Input: AWS Index CSV
    Output: 2 dataframes, one with sponsoring org details,
            one with grantee data
    '''
    sponsors = pd.DataFrame()
    grants_made = pd.DataFrame()

    daf_object_ids = []
    failures  = []


    # for daf_file in os.listdir(file_or_folder):
    for file_location in file_or_folder:
        if os.path.isdir(file_location):
            file_count = 0
            start = time.time()
            for daf_file in os.listdir(file_location):
                tree = rd.read_form(document= file_location + '/' + daf_file, download=False)
                if rd.get_form_type(tree) == '990':
                    try:
                        if rd.confirm_daf_fund(tree):
                            daf_object_ids.append(daf_file)
                            sponsor_details, grantees = get_daf_data(tree, verbose)
                            
                            #append dataframes with org info and grantees (I)
                            sponsors = sponsors.append(sponsor_details)
                            grants_made = grants_made.append(grantees)

                        else:
                            pass
                    except Exception as e:
                        #print(e)
                        failures.append(daf_file)
                else:
                    pass

                if file_count == end:
                    break
                file_count += 1 
                
                if file_count % 100000 == 0:

                    print(file_count, 'files counted in', (time.time() - start) / 60, 'minutes')



        else:
            index = pd.read_csv(file_or_folder)
            # collect only 990s
            # initially RETURN_TYPE is stored as text; after converting to DataFrame,
            # it is considered a numpy int64, which may cause a warning if you convert
            # a selection of forms from the csv to a DataFrame and back to a CSV. 
            if type(index['RETURN_TYPE']) != str: 
                index = index.loc[index['RETURN_TYPE'] == 990].OBJECT_ID.tolist()
            else:
                index = index.loc[index['RETURN_TYPE'] == '990'].OBJECT_ID.tolist()
        
            for form in index[start:end]:
                link = "https://s3.amazonaws.com/irs-form-990/{}_public.xml".format(str(form))
                tree = rd.read_form(document=link, download=True)
                if rd.confirm_daf_fund(tree):
                    daf_object_ids.append(form)
                    sponsor_details, grantees = get_daf_data(tree, verbose)
                    #append dataframes with org info and grantees (I)
                    sponsors = sponsors.append(sponsor_details)
                    
                    if grantees:
                        # Schedule I may not exist for some organizations
                        grants_made = grants_made.append(grantees)
                    else:
                        pass
                else:
                    pass


    grants_made.to_csv("Grantees.csv", index=False)
    sponsors.to_csv("Sponsors.csv", index=False)

    with open('DAF_Object_IDS.txt', 'w') as f:
        for daf in daf_object_ids:
            f.write("{}\n".format(str(daf)))

    with open('Failures.txt', 'w') as f:
        for daf in failures:
            f.write("{}\n".format(str(daf)))

    return None

def get_daf_data(tree, verbose):
    #confirm DAF
    if rd.confirm_daf_fund(tree):
        if verbose:
            print("DAF Confirmed. Getting data...")
        #get org headers
        sponsor = rd.get_form_headers(tree)
        #get schedule D
        daf_details = rd.get_schedule_d(tree)
        #combine headers and schedule D
        #sponsor_details = pd.DataFrame({**sponsor, **daf_details}, index=[0])

        #get schedule I
        grantees = rd.get_schedule_i(tree)
        #clean schedule I for database loading
        if grantees is not None:
            grantees = rd.clean_daf_grantee_data(grantees, sponsor['EIN'], sponsor['TAXYEAR']) 

        return (sponsor_details, grantees)
    else:
        return None

#################
# CODE ANALYSIS #
#################
'''
Check form versions and types to analyze issues that arise
'''
def filing_type(file_or_folder, end):
    '''
    Creates a DataFrame to summarize form type and version
    '''
    data = {'Version':[], 'Type':[]}
    for file_location in file_or_folder:
        if os.path.isdir(file_location):
            count = 0
            for daf_file in os.listdir(file_location):
                tree = rd.read_form(document= file_location + '/' + daf_file, download=False)
                data['Type'].append(rd.get_form_type(tree))
                data['Version'].append(rd.get_form_version(tree))
                count += 1
                if count == end:
                    break

    pd_data = pd.DataFrame(data)
    pd_data.to_csv('990_Versions_Types.csv')

    return pd_data.describe()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Read an AWS IRS 990 Index and download data \
                        associated with a donor-advised fund')
    parser.add_argument('-file',type=str, nargs='*',
                    help='file to use, either a folder or a csv')
    parser.add_argument('-start',type=int, default=0,
                    help='object id index to start with')
    parser.add_argument('-end',type=int, default=500000,
                    help='object id index to end with')
    parser.add_argument('--verbose', action="store_true",
                    help="whether to print progress")
    parser.add_argument('--analyze', action="store_true",
                    help="Check version and form types")        
    args = parser.parse_args()   
    if args.analyze:
        filing_type(args.file, args.end)
    else:
        get_data(args.file, args.start, args.end, args.verbose)