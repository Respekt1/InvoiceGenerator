#!/usr/bin/env python
"""
Simple script to generate PDF invoices, encrypt & email to clients.
"""

import gnupg
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import fpdf
import yaml
import datetime

fh = open('config.yaml', 'r')
config = yaml.load(fh)

gpg_home = config['gnupg_homedir']
companies_house_api = config['companies_house_api']
companies_house_api_key = config['companies_house_api_key']

gpg = gnupg.GPG(homedir=gpg_home)
gpg.encoding = 'utf-8'


def encrypt_file():
    '''
    Blah
    '''
    pass


def generate_pdf(company):
    '''
    Blah
    '''
    print("Generating PDF Invoice..") 
    pdf = fpdf.FPDF()
    pdf.add_page()

    # Title Top
    pdf.set_font("Arial", size=18)
    pdf.set_text_color(0, 101, 135)
    pdf.cell(0, 10, config['business_name'], 0, 0, 'L')
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    pdf.output("invoice-{}-{}.pdf".format(today, company['Name'].replace(' ', '_')))


def get_companies_house_info(s):
    '''
    Blah
    '''
    active_companies = []
    r = requests.get( companies_house_api, params={'q':s}, auth=HTTPBasicAuth(companies_house_api_key,''))
    results = r.json()['items']
    for company in results:
        if company['company_status'] == 'active':
            active_companies.append(company)

    return active_companies



def main():
    '''
    Main
    '''

    client = raw_input('Who are you invoicing?: ')
    active_companies = get_companies_house_info(client)
    
    for index, co in enumerate(active_companies):
        print("{}:\t{}\n\t{}".format(index, co['title'], co['snippet']))

    selection = raw_input("Choose the index for the correct company, or type a custom name: ")
    
    if selection.isdigit():
        selection = int(selection)
        print("Company {}, has been selected.".format(active_companies[selection]['title']))
        invoiced_client = {'Name':active_companies[selection]['title'], 'Address': active_companies[selection]['snippet']}
    else:
        invoiced_client = {'Name': selection}
        invoiced_client['Address'] = raw_input('What is the address of {}?: '.format(selection))
    
    generate_pdf(invoiced_client)
    


if __name__ == '__main__':
    main()
