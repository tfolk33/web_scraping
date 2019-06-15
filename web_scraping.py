import requests

from bs4 import BeautifulSoup
from csv import writer

import csv
import sqlite3

response = requests.get('https://www.xome.com/homes-for-sale/UT/Park-City')

soup = BeautifulSoup(response.text, 'html.parser')

properties = soup.find_all(class_='listview-result')

with open('properties.csv', 'w') as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Address', 'Price']
    csv_writer.writerow(headers)

    for property in properties:
        address = property.find(itemprop='streetAddress').get_text().replace('\n', '').replace('\t', '').replace(' ', '')
        price = property.find(class_='listview-price').get_text().replace('\n', '')
        # sqFeet = post.find(class_='listview-address').get_text().replace('\n', ''))
        csv_writer.writerow([address, price])

con = sqlite3.connect("PropertyData.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS Properties (Address, Price);") # use your column names here

with open('properties.csv','rt') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['Address'], i['Price']) for i in dr]

cur.executemany("INSERT INTO Properties (Address, Price) VALUES (?, ?);", to_db)
con.commit()
con.close()