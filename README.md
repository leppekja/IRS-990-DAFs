# 990-DAFs
Code for analyzing Donor Advised Funds 

## Overview

Donor Advised Funds (DAF) are some of the largest nonprofit organizations in the world, distributing billions of dollars to NGOs each year. This project attempts to map and analyze the flow of these funds from DAFs to NGOs. DAFs are required to report any cumulative grants greater than $5,000 in the IRS 990 Form Schedule I. 


### Step 1 - COMPLETE

Code for reading XML [Schedule I](https://www.irs.gov/pub/irs-pdf/f990si.pdf) forms. Files are available in XML format from multiple locations, including AWS (easily accessible through [open990.org](https://www.open990.org/org/680480736/network-for-good-inc/)). Need to collect, for each organization, the name, address, EIN, IRS organization type e.g. 501(c)(3), and amount of grant, with a indicator for which DAF the funds were distributed through. Will read this data into a Pandas Dataframe for analysis. 

### Step 2 - INCOMPLETE

Iterate through all 990 forms and select those with a donor advised fund. Collect object IDs and gather into a file for further analysis.

### Step 3 - INCOMPLETE

Use code from Step 1 to read in all organizations collected in step 2. Output will be a data frame with details on all sponsoring organizations (those with a DAF) and a dataframe with all nonprofit organizations that received gifts > $5,000.

### Resources

https://ips-dc.org/report-gilded-giving/
https://fas.org/sgp/crs/misc/R42595.pdf
https://www.philanthropy.com/article/What-Donor-Advised-Funds/156495
https://stackabuse.com/reading-and-writing-xml-files-in-python/
https://s3.amazonaws.com/irs-form-990/201941789349300019_public.xml
https://www.open990.org/org/680480736/network-for-good-inc/
https://docs.opendata.aws/irs-990/readme.html