# 990-DAFs
Code for analyzing Donor Advised Funds 

Thanks for visiting! Our data is currently being reviewed to ensure the highest level of accuracy possible. We expect functionality to be enabled winter 2020.

![Landing Page photo](/UI Designs/home_page.png)

### Table of Contents

- [Overview](#overview)
- [Example Use Cases](#example-use-cases)
- [Step 1](#step-1)
- [Step 2](#step-2)
- [Step 3a](#step-3a)
- [Step 3b](#step-3b)
- [Step 4](#step-4)
- [Step 5](#step-5)
- [Step 6](#step-6)
- [About the 990 Forms, Versions, and Types](#about-the-990-forms-versions-and-types)
- [Issues](#issues)
- [Next Steps](#next-steps)
- [IRS 990 Questions](#irs-990-questions)
- [What is the Schedule I?](#what-is-the-schedule-i)
- [Resources](#resources)

## Overview

Donor Advised Funds (DAF) distribute billions of dollars to NGOs each year. This project attempts to map and analyze the flow of these funds from DAFs to NGOs. DAFs are required to report any cumulative grants greater than $5,000 in the IRS 990 Form Schedule I. This project also attempts to demonstrate the validity of open source data projects for the nonprofit sector.

### Example Use Cases

- Identify which nonprofits obtain the most grants from donor-advised funds. 
- Identify top donor-advised funds

![map photo](/UI Designs/map.png)

- Examine various measures of grant spread, i.e., how diverse are the grantees across organization size, geographic area, mission or cause, etc.

![Report page photo](/UI Designs/report.png)

### Step 1
##### COMPLETE

Code for reading XML [Schedule I](https://www.irs.gov/pub/irs-pdf/f990si.pdf) forms. Files are available in XML format from multiple locations, including AWS (easily accessible through [open990.org](https://www.open990.org/org/680480736/network-for-good-inc/)). Need to collect, for each organization, the name, address, EIN, IRS organization type e.g. 501(c)(3), and amount of grant, with a indicator for which DAF the funds were distributed through. Will read this data into a Pandas Dataframe for analysis. The [Community Concordance](https://nonprofit-open-data-collective.github.io/irs-efile-master-concordance-file/) allows us to map field locations across many versions of the 990. We are working with variables labeled PC, as well as the header. The paths for the Schedule-D information do change depending on the version.

read_990.py contains functions to query an XML document. From the command line:

    python read_990.py -form 'https://s3.amazonaws.com/irs-form-990/201541349349307794_public.xml' --download --verbose

read_990s_dafs_file contains a function to read through an AWS index file and aggregate DAF data. From the command line:

    python read_990s_dafs_file.py -file 'index_2018.csv'

Optional arguments <start> and <end> allow selection by index. 

### Step 2
##### COMPLETE

Iterate through all 990 forms and select those with a donor advised fund. Collect object IDs and gather into a file for further analysis.

IRS 990 Forms in XML can be downloaded [in bulk from AWS](https://docs.opendata.aws/irs-990/readme.html) using the [AWS CLI](https://docs.aws.amazon.com/cli/index.html). This was the simplest (probably least efficient also) command I could find, downloading only forms from 2018:

    aws s3 sync s3://irs-form-990/ ./<local file here> --exclude "*" --include "2018*"

Otherwise, you can download the index for each year and manually select individual forms at https://s3.amazonaws.com/irs-form-990/index_ **specific year here**.csv. These files are also accessible in JSON format. Note that according to Applied Nonprofit Research, this is [unreliable](https://appliednonprofitresearch.com/posts/2020/06/skip-the-irs-990-efile-indices/).

### Step 3a
##### COMPLETE

Use code from Step 1 to read in all organizations collected in step 2. Output will be a data frame with details on all sponsoring organizations (those with a DAF) and a dataframe with all nonprofit organizations that received gifts > $5,000.

fields.csv contains the fields and variable descriptions for those collected within the scope of this analysis. This is a work in progress and may be updated to account for differing versions. 

### Step 3b
##### COMPLETE

We need to read the data into a database accessible online for the web application. We're using a PostgreSQL database on AWS RDS. create.sql is an outdated psql script to create the schema; the primary schema is implemented through Django's Model classes (will be uploaded later). A ERD diagram is in daf_erd_diagram_sketch.png and will be updated soon. 

### Step 4
##### COMPLETE

We need to geocode the addresses of both the sponsoring organizations and the grantees. 

### Step 5
##### INCOMPLETE

Set up web search application to easily search an organization and get back either:

- the organizations that it has funded through a donor-advised fund
- the donor-advised funds that have supported that organization
- ranking (for DAFs, in terms of funds given; for nonprofits, in terms of funds recieved)
- visualization of where funds have been sent/recieved. 

For this application, we're using a Django framework hosted on AWS Lightsail. 

Deployment instructions:
- https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Deployment
- https://aws.amazon.com/getting-started/hands-on/deploy-python-application/
- https://stackoverflow.com/questions/63680664/no-apps-folder-on-django-lightsail/63684039#63684039
- https://docs.bitnami.com/aws/infrastructure/django/get-started/start-django-project/
- https://docs.bitnami.com/aws/infrastructure/django/get-started/deploy-django-project/

### Step 6
##### INCOMPLETE

Write up summary of findings.

### About the 990 Forms, Versions, and Types

The purpose of this analysis is to analyze the flow of funds from donor-advised funds to nonprofit organizations. 

990EZ forms are not applicable for this analysis. See the [2019 version, Part V, line 44a](https://www.irs.gov/pub/irs-pdf/f990ez.pdf), which informs the filer that if donor-advised funds were maintained, the filer must use Form 990. This form is meant for organizations with '[gross receipts of less than $200,000 and total assets of less than $500,000 at the end of their tax year.](https://www.irs.gov/pub/irs-pdf/i990ez.pdf)'

990PF forms are for private foundations to complete. These forms only address donor-advised funds in [Part VII-A, Statements Regarding Activities, line 12](https://www.irs.gov/pub/irs-pdf/f990pf.pdf#page=4&zoom=auto,-266,18), asking "Did the foundation make a distribution to a donor advised fund over which the foundation or a disqualified person had advisory privileges? If 'Yes', attach statement." The [form instructions](https://www.irs.gov/pub/irs-pdf/i990pf.pdf#page=25&zoom=auto,-206,552) note the show whether this was treated as a qualifying distribution, and to "explain how the distributions will be used to accomplish a purpose described in section 170(c)(2)(B)".

Note that a private foundation may control a donor-advised fund, but these organizations would then need to file a 990, rather than a 990PF (to the best of my understanding). Right now, I am only using the 990 forms. 

### ISSUES

##### ETL
- Different form versions break the code
##### Data Questions
- A number of organizations marked Yes as maintaining a DAF or similar fund without completing summary information in Schedule D part 1. See [Winona State University Foundation June 2018 Filing](https://s3.amazonaws.com/irs-form-990/201800349349300310_public.xml). Unclear whether this is an oversight, or there is some reason this is fine. 
- Improper EIN recorded in 2018 data (Recipient EIN listed as 883682); likely others.
##### Data Cleaning
- Need to read other years' filings as well, likely will be field changes. Use Open Data Collective's Concordance?
- Scholarship support is incorrectly recorded as of now.
- Adjust address issues; make sure line 1 and 2 are joined. Note also issues with 'c/o NAME' in the AddressLine1Txt field like in [this form](https://s3.amazonaws.com/irs-form-990/201900089349300935_public.xml).
##### Batch Testing 
- db.py uploads a batch file of Sponsors to a database, however, Django/PSQL does not maintain order of columns upon updating. If the model is changed, the .csv column order may have to be updated to. Have to check the table schema to be sure. 
- Data needs improved cleaning / database needs to account for these. irs_section_desc allows for 10 varchar, ein 46001406 included a city for this field.
- Batch csv upload, when filling the donation table, cannot find all the sponsor ein for some reason. May have been deleted through data cleaning? 223089640, for example. 
##### Website Design
- Django Model in sponsor_detail seems to identify the organization name as organization.grantee_ein
- Navigation bar does not collapse in for small screens; need to make mobile friendly
- Implement summary queries for total amount recieved/given for organizations
- Javascript for giving over the years charts not set up
##### Solved
- Get all lines of business name txt - SOLVED
- Only record 990 data - SOLVED
- Schedule D endowment returning - SOLVED
- Grantee supplementary Schedule I information returning - SOLVED
- What are *FundsAndOtherAccountsHeld*? Should these be included? - SOLVED (mostly)
- Need to add year for different tax returns / grants. Composite primary keys don't work with Django? -SOLVED
- Organization may file two tax returns in a single year, which results in a database issue if the EIN is used as a primary key. See, for instance, EIN 910668368, which filed in 2018 both for the 2016-2017 and 2017-2018 tax years. This is really only relevant if syncing with the AWS database and filtering by the year Object_id, as well as the batch uploading from csv file in db.py. - SOLVED

See [here](https://www.irs.gov/instructions/i990sd), in the **Exceptions** section. As of now, they are included. It is unclear whether grants mades from these types of funds are listed on the Schedule I, so if anyone knows, please reach out!  

- Indicating yes on DAF does not imply existence of Schedule I for a minority of organizations, see EIN 626047769, Jun 2017 filing. - SOLVED

### Next Steps

- Geocode grantee and sponsoring organizations addresses - Done
- Develop interactive online map - Done
- Enable Rest API access
- Create automatic monthly updating from IRS updates; what is the best ETL pipeline?
- Automatic report generation for organizations and sector-wide

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
