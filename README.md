# ICS Place Based Allocation Tool 

### About the Project

This repository holds a tool built in Python to assist Integrated Care Systems (ICSs) to perform need based allocation based on defined place. It uses the most recently produced GP Registered Practice Populations as well as the weighted populations calculated from the Allocation model for each of its components. More information on the Allocations process, as well as useful documentation can be found at https://www.england.nhs.uk/allocations/

_**Note:** Only public data shared in this repository._

### Built With

[![Python v3.8](https://img.shields.io/badge/python-v3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
- [Streamlit](https://pypi.org/project/streamlit/)

### Getting Started

#### Installation

To get a local copy up and running follow these simple steps.

To clone the repo:

`git clone https://github.com/nhsx/SynthVAE.git`

To create a suitable environment:
- ```python -m venv .venv```
- `source .venv/bin/activate`

To load all dependencies
- `pip install -r requirements.txt`

To run the tool
- `streamlit run allocation_tool.py`

Streamlit will then render the tool and display it in your default web browser. When run in this way, any changes to the script in your editor will change the app running locally. 

More information about Streamlit can be found from the following link: 
https://docs.streamlit.io/en/stable/  

The .streamlit directory contains configuration settings that affect the appearance of the application when it is deployed. 

## Usage

The tool is deployed from a GitHub repository using Streamlit's sharing service. To make changes to the deployed app, push changes that have been made to the source code to the GitHub repository, these changes will then be reflected in the app.  
Full instructions for using the tool can be found in the user guide. The tool allows 'place' to be defined in an ICS as a cluster of GP practices. This allows place to be flexibly defined, whether that is as GP practices in the same Primary Care Network (PCN), Local Authority or that feed into the same Secondary services for example, that is at the discretion of the ICS. Once GP practices have been allocated to place, the relative need indices can be calculated and the output can be downloaded as a CSV. The underlying data for the tool is pulled from the Excel workbook in the repository, gp_practice_weighted_population.xlsx. When new allocations are calculated or updates are made to GP Practice populations, the tool can be updated by replacing this workbook with one containing the new data, ensuring to maintain the same file name. The tool is resilient to changes in rows in this spreadsheet but any changes to column names or column order from the previous version may lead to issues and this will have to be debugged. 

## Support 

Enquiries about the overall allocation process can be directed to: england.revenue-allocations@nhs.net.

Tool owners would like to acknowledge the contributions and support from NHSX Analytics Unit to get this up and running. 

## Copyright and License

Unless otherwise specified, all content in this repository and any copies are subject to [Crown Copyright](http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/copyright-and-re-use/crown-copyright/) under the [Open Government License v3](./LICENSE).

Any code is dual licensed under the MIT license and the [Open Government License v3](./LICENSE). 

Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL-licensed or AGPL-licensed libraries, as these would violate the terms of those libraries' licenses.****
