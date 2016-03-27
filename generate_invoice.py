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


def encrypt_file(file_name):
    '''
    Blah
    '''

    public_keys = gpg.list_sigs()

    for index, key in enumerate(public_keys):
        print("{}\t{}\n\t{}".format(index, key['uids'][0], key['keyid']))
        
    ans = raw_input('Which key do you wish to encrypt your invoice with?: ')


    print("Encrypting file..")

    with open(file_name, 'rb') as f:
        status = gpg.encrypt(
            f, config['my_gpg_pub_id'], public_keys[int(ans)]['keyid'],
            output = file_name+'.gpg')

    print 'ok: ', status.ok
    print 'status: ', status.status
    print 'stderr: ', status.stderr


def generate_pdf(company):
    '''
    Blah
    '''
    print("Generating PDF Invoice..") 
    pdf = fpdf.FPDF()
    pdf.add_page()
    
    # Border
    pdf.rect(5.0, 5.0, 200.0, 280.0)

    # Title Top
    pdf.set_font("Arial", size=18)
    pdf.set_text_color(0, 101, 135)
    pdf.cell(0, 10, config['business_name'], 0, 0, 'L')
    pdf.cell(0, 10,'INVOICE', 0, 1, 'R')
    pdf.ln(10)

    # Left client info
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10,'INVOICE TO:', 0, 0, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(7)
    pdf.cell(0, 10,company['Name'], 0, 0, 'L')
    pdf.ln(7)
    pdf.cell(0, 10,company['Address'], 0, 1, 'L')
    pdf.ln(15)

    # Top right summary box
    pdf.set_fill_color(0, 101, 135)
    pdf.rect(110, 55, 90.0, 25.0,style = 'F')
    pdf.set_fill_color(0, 101, 135)
    pdf.set_font("Arial", size=8)
    pdf.set_xy(120.0, 60.0)
    pdf.cell(20, 0,'Invoice No', 0, 0, 'L')
    pdf.set_xy(150.0, 60.0)
    pdf.cell(20, 0,'Invoice Date', 0, 0, 'L')
    pdf.set_xy(170.0, 60.0)
    pdf.cell(20, 0,'Total', 0, 0, 'L')
    pdf.ln(7)
    pdf.set_font("Arial", size=10)
    pdf.set_xy(120.0, 70.0)
    pdf.cell(20, 0,'0005', 0, 0, 'L')
    pdf.set_xy(150.0, 70.0)
    pdf.cell(20, 0,'28 Mar 2016', 0, 0, 'L')
    pdf.set_xy(170.0, 70.0)
    pdf.cell(20, 0,'240', 0, 0, 'L')

    # Main itemised list box
    pdf.set_font("Arial", size=12)
    pdf.set_xy(10.0, 100.0)
    pdf.cell(20, 0,'DESCRIPTION', 0, 0)
    pdf.set_xy(60.0, 100.0)
    pdf.cell(20, 0,'QTY', 0, 0)
    pdf.set_xy(80.0, 100.0)
    pdf.cell(20, 0,'UNIT', 0, 0)
    pdf.set_xy(100.0, 100.0)
    pdf.cell(20, 0,'NET', 0, 0)
    pdf.set_xy(120.0, 100.0)
    pdf.cell(20, 0,'VAT', 0, 0)
    pdf.set_xy(140.0, 100.0)
    pdf.cell(20, 0,'VAT TOTAL', 0, 0)
    pdf.set_xy(180.0, 100.0)
    pdf.cell(20, 0,'TOTAL', 0, 0)

    
    # Banking information


    # Footer/botto,
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    pdf_file_name = "invoice-{}-{}.pdf".format(today, company['Name'].replace(' ', '_'))
    pdf.output(pdf_file_name)

    return pdf_file_name


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
    
    file_name = generate_pdf(invoiced_client)

    if raw_input("Do you wish to encrypt your invoice? y/n: ") == 'y':
        encrypt_file(file_name)
    else:
        print('No encrypting file: {}'.format(file_name))
    

if __name__ == '__main__':
    main()
