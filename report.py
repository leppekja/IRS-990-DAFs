'''

Code for creating Sponsoring Organization and Grantee reports for DonorAdvisedFunds.io

'''

def sponsor_report():
    '''
    Input:
        Sponsoring organization EIN
    Returns the following statistics and visualizations, 
    depending on given arguments:
    ---------------SINGLE ORGANIZATION---------
        ### DATA POINTS ###
            REPORTED YEARLY FOR EACH YEAR THAT DATA IS AVAILABLE
            Tax Year

            Total amount contributed across all DAF accounts at an organization
            Total amount granted across all DAF accounts at an organization
            Total worth at End of Year across all DAF accounts at an organization
            Number of DAF accounts held at an organization
            Whether the organization made a legal disclosure to all contributers
            Whether the organization informed donors of grant purpose

            Number of similar accounts held  at an organization
            Total amount contributed across all similar accounts at an organization
            Total amount granted across all similar accounts at an organization
            Total worth at End of Year across all similar accounts at an organization        

        ### SUMMARY STATISTICS ###
            REPORTED YEARLY FOR EACH YEAR THAT DATA IS AVAILABLE
            Average amount held in each DAF account
                (Total EOY DAF worth / Number of DAF held)
                # Calculate mode and median as well

            NOT YEARLY; CUMULATIVE ACROSS ALL YEARS DATA IS AVAILABLE
            Cumulative amount contributed across all accounts
            Cumulative amount granted across all accounts
    --------------SECTOR REPORT------------------
        ### Data Points ###
            REPORTED YEARLY FOR EACH YEAR THAT DATA IS AVAILABLE 
            Total Number of DAF accounts 
            Total Amount contributed to DAF accounts
            Total Amount granted from DAF accounts
            Total EOY Worth for all organizations

            Total Number of similar accounts
            Total Amount contributed to similar accounts
            Total Amount granted from similar accounts
            Total EOY Worth for all organizations    
        ### SUMMARY STATISTICS ###
            REPORTED YEARLY FOR EACH YEAR THAT DATA IS AVAILABLE
            % Change in number of DAF accounts 
            % change in amount contributed to DAF accounts
            % change in amount granted from DAF accounts
            % change in Total EOY Worth 
            
            % Change in number of similar accounts
            % change in Amount contributed to similar accounts
            % change Amount granted from similar accounts
            % change EOY Worth for all organizations

            Average amount held in each DAF account
                (Total EOY Worth (sector) / Number of all DAF accounts)
                    # Calculate mode and median as well

            NOT YEARLY; CUMULATIVE ACROSS ALL YEARS DATA IS AVAILABLE
            Cumulative amount contributed across all accounts
            Cumulative amount granted across all accounts


        VISUALIZATIONS
    '''
