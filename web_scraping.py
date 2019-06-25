from bs4 import BeautifulSoup
from csv import writer

import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

browser = webdriver.Chrome()

browser.get("https://www.xome.com/auctions/bank-owned")
time.sleep(1)

elem = browser.find_element_by_tag_name("body")

no_of_pagedowns = 15

while no_of_pagedowns:
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    no_of_pagedowns-=1

post_elems = browser.find_elements_by_class_name("property-card-photo")

print(len(post_elems))
#for post in post_elems:
#    print(post.text)

#############################################

# from requests_html import HTMLSession

# import HTMLSession from requests_html
# from requests_html import HTMLSession
 
# # create an HTML Session object
# session = HTMLSession()

# # Use the object above to connect to needed webpage
# resp = session.get("https://www.xome.com/auctions/bank-owned")
 
# # Run JavaScript code on webpage
# resp.html.render(timeout=30)

# import csv
# import sqlite3

# listings = BeautifulSoup(resp.html.html, 'html.parser')
# results = listings.find(class_="property-card-photo")
# # listings = results.find_all(class_="col-md-4 col-sm-6 col-xs-12 sr-property-card-holder")

# # print(resp.status_code)
# print(len(results))
#for result in results:
#    print(listing)

 #with open('properties.csv', 'w') as csv_file:
    # csv_writer = writer(csv_file)
    # headers = ['Address', 'City', 'Zip Code', 'State', 'Starting Bid', 
    # 'Reserve Met', 'Resreve Price', 'Property Type', 'Beds', 'Square Footage', 'Pictures'
    #  'Property Id', 'URL', 'Auction Start Time', 'Payment Type', 'Listing Agent Info',
    #   'Event Name', 'Event Details', 'Property Details', 'Listing Information', 'Auction Disclaimers',
    #    'Price History', 'Tax History', 'Current Market Trends', 'Rental Info']

    # address = listing.find(class_="address-line-1").get_text()
    # city = listing.find(id="crumb4")
    # city = city.find("a").get_text()
    # csv_writer.writerow(headers)
    # csv_writer.writerow([address, city])

    # for property in properties:
    #    address = property.find(itemprop='streetAddress').get_text().replace('\n', '').replace('\t', '').replace(' ', '')
    #    csv_writer.writerow([address, price])

# Tansfer to SQL db
# con = sqlite3.connect("PropertyData.db")
# cur = con.cursor()
# cur.execute("CREATE TABLE IF NOT EXISTS Properties (Address, Price);") # use your column names here

# with open('properties.csv','rt') as fin: # `with` statement available in 2.5+
#     # csv.DictReader uses first line in file for column headings by default
#     dr = csv.DictReader(fin) # comma is default delimiter
#     to_db = [(i['Address'], i['Price']) for i in dr]

# cur.executemany("INSERT INTO Properties (Address, Price) VALUES (?, ?);", to_db)
# con.commit()
# con.close()