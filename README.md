# 990-DAFs
Code for analyzing Donor Advised Funds 

## Overview

Donor Advised Funds (DAF) are some of the largest nonprofit organizations in the world, distributing billions of dollars to NGOs each year. This project attempts to map and analyze the flow of these funds from DAFs to NGOs. DAFs are required to report any cumulative grants greater than $5,000 in the IRS 990 Form Schedule I. This project also attempts to demonstrate the validity of open source data projects for the nonprofit sector.

### Example Use Cases

- Identify which nonprofits obtain the most grants from donor-advised funds. 
- Identify top donor-advised funds
- Examine various measures of grant spread, i.e., how diverse are the grantees across organization size, geographic area, mission or cause, etc. 

### Step 1 - COMPLETE

Code for reading XML [Schedule I](https://www.irs.gov/pub/irs-pdf/f990si.pdf) forms. Files are available in XML format from multiple locations, including AWS (easily accessible through [open990.org](https://www.open990.org/org/680480736/network-for-good-inc/)). Need to collect, for each organization, the name, address, EIN, IRS organization type e.g. 501(c)(3), and amount of grant, with a indicator for which DAF the funds were distributed through. Will read this data into a Pandas Dataframe for analysis. 

read_990.py contains functions to query an XML document. From the command line:

    python read_990.py -form 'https://s3.amazonaws.com/irs-form-990/201541349349307794_public.xml' --download --verbose

read_990s_dafs_file contains a function to read through an AWS index file and aggregate DAF data. From the command line:

    python read_990s_dafs_file.py -file 'index_2018.csv'

Optional arguments <start> and <end> allow selection by index. 

### Step 2 - COMPLETE

Iterate through all 990 forms and select those with a donor advised fund. Collect object IDs and gather into a file for further analysis.

IRS 990 Forms in XML can be downloaded [in bulk from AWS](https://docs.opendata.aws/irs-990/readme.html) using the [AWS CLI](https://docs.aws.amazon.com/cli/index.html). This was the simplest command I could find, downloading only forms from 2018:

    aws s3 sync s3://irs-form-990/ ./<local file here> --exclude "*" --include "2018*"

Otherwise, you can download the index for each year and manually select individual forms at https://s3.amazonaws.com/irs-form-990/index_ **specific year here**.csv. These files are also accessible in JSON format. Note that according to Applied Nonprofit Research, this is [unreliable](https://appliednonprofitresearch.com/posts/2020/06/skip-the-irs-990-efile-indices/).


### Step 3a - COMPLETE

Use code from Step 1 to read in all organizations collected in step 2. Output will be a data frame with details on all sponsoring organizations (those with a DAF) and a dataframe with all nonprofit organizations that received gifts > $5,000.

fields.csv contains the fields and variable descriptions for those collected within the scope of this analysis. This is a work in progress and may be updated to account for differing versions. 

### Step 3b - INCOMPLETE

We need to read the data into a database accessible online for the web application. 

### Step 4 - INCOMPLETE

We need to geocode the addresses of both the sponsoring organizations and the grantees. 

### Step 5 - INCOMPLETE

Set up web search application to easily search an organization and get back either:
a) the organizations that it has funded through a donor-advised fund
b) the donor-advised funds that have supported that organization
c) ranking (for DAFs, in terms of funds given; for nonprofits, in terms of funds recieved)

### Step 6 - INCOMPLETE

Write up summary of findings.

### About the 990 Forms, Versions, and Types

The purpose of this analysis is to analyze the flow of funds from donor-advised funds to nonprofit organizations. 

990EZ forms are not applicable for this analysis. See the [2019 version, Part V, line 44a](https://www.irs.gov/pub/irs-pdf/f990ez.pdf), which informs the filer that if donor-advised funds were maintained, the filer must use Form 990. This form is meant for organizations with '[gross receipts of less than $200,000 and total assets of less than $500,000 at the end of their tax year.](https://www.irs.gov/pub/irs-pdf/i990ez.pdf)'

990PF forms are for private foundations to complete. These forms only address donor-advised funds in [Part VII-A, Statements Regarding Activities, line 12](https://www.irs.gov/pub/irs-pdf/f990pf.pdf#page=4&zoom=auto,-266,18), asking "Did the foundation make a distribution to a donor advised fund over which the foundation or a disqualified person had advisory privileges? If 'Yes', attach statement." The [form instructions](https://www.irs.gov/pub/irs-pdf/i990pf.pdf#page=25&zoom=auto,-206,552) note the show whether this was treated as a qualifying distribution, and to "explain how the distributions will be used to accomplish a purpose described in section 170(c)(2)(B)".

Note that a private foundation may control a donor-advised fund (to the best of my understanding). 

### ISSUES

- Get all lines of business name txt
- Different form versions break the code
- Only record 990 data - SOLVED
- Indicating yes on DAF does not imply existence of Schedule I for a minority of organizations, see EIN 626047769, Jun 2017 filing. - SOLVED
- Improper EIN recorded in 2018 data (Recipient EIN listed as 883682); likely others.
- Need to read other years' filings as well

### Next Steps

- Geocode grantee and sponsoring organizations addresses
- Develop interactive online map 
- Create automatic monthly updating from IRS updates
- Host search site for organizations funded through grants from DAFs

### IRS 990 Questions

- Confirm disclosure requirements for donor-advised funds and write-up?

### What is the Schedule I?

As [found here](https://www.irs.gov/pub/irs-pdf/f990si.pdf#page=3&zoom=auto,-336,738), the IRS Form 990 Schedule I is "used by an organization that files Form 990 to provide information on **grants and other assistance** made by the filing organization during the **tax year** to **domestic organizations, domestic governments,** and **domestic individuals.**...*Grants and other assistance* include awards, prizes, **contributions**, noncash assistance, cash allocations, stipends, scholarships, fellowships, research grants, and similar payments and distributions made by the organization during the tax year."

**Important!**

Information is only reported in a Schedule I "for each recipient domestic organization or domestic government that received more that $5,000 aggregate of grants or assistance from the organization during the tax year".

Schedule I does not include any grants or assistance provided to organizations, including domestic, for the purpose of aiding a foreign organization, government, or individual. 

### Resources

[Many repositories](https://github.com/search?q=irs-990&type=) offer code on reading IRS 990 XML files to databases / individually.

- https://www.grantmakers.io/
- https://ips-dc.org/report-gilded-giving/
- https://fas.org/sgp/crs/misc/R42595.pdf
- https://www.philanthropy.com/article/What-Donor-Advised-Funds/156495
- https://stackabuse.com/reading-and-writing-xml-files-in-python/
- https://s3.amazonaws.com/irs-form-990/201941789349300019_public.xml
- https://www.open990.org/org/680480736/network-for-good-inc/
- https://docs.opendata.aws/irs-990/readme.html