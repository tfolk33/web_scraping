from bs4 import BeautifulSoup
from csv import writer

import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# browser = webdriver.Chrome()

# browser.get("https://www.xome.com/auctions/bank-owned")
# time.sleep(1)

# elem = browser.find_element_by_tag_name("body")

# def scroll():
#     scroll_delay = 15
#     last_height = browser.execute_script("return document.body.scrollHeight")

#     while True:
#         # Action scroll down
#         # elem.send_keys(Keys.END)
#         browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(scroll_delay)
#         new_height = browser.execute_script("return document.body.scrollHeight")
            
#         if new_height == last_height:
#             break
#         last_height = new_height

def cleanString(input):
    count = 0
    for letter in str(input):
        if letter.isalpha() or letter.isdigit():
            break
        else:
            count += 1
    input = str(input[count:])
    revinp = reversed(input)
    count = 0
    for letter in revinp:
        if letter.isalpha() or letter.isdigit():
            break
        else:
            count += 1
    input = input[:-count]
    return input

def getZip(zip):
    reversedzip = reversed(zip)    
    count = 0
    for letter in reversedzip:
        if letter.isdigit():
            count += 1
        else:
            break    
    zip = zip[-count:]
    zip = re.sub("\D", "", zip)
    return zip   

# while True:
#     scroll()
#     try:
#         link = browser.find_element_by_link_text('Click here')
#         browser.implicitly_wait(5)
#         link.click()
#     except:
#         break

# post_elems = browser.find_elements_by_class_name("property-card-photo")

# print(len(post_elems))
#for post in post_elems:
#    print(post.text)

#############################################

from requests_html import HTMLSession 
# create an HTML Session object
session = HTMLSession()
# Use the object above to connect to needed webpage
resp = session.get("https://www.xome.com/auctions/236-Fairview-Cr-Xenia-OH-45385-312842139")
# Run JavaScript code on webpage
resp.html.render(timeout=480)

import csv
import sqlite3
import re

listing = BeautifulSoup(resp.html.html, 'html.parser')

with open('properties.csv', 'w') as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Address', 'City', 'Zip Code', 'State', 'Starting Bid', 
        'Reserve Met', 'Resreve Price', 'Property Type', 'Beds', 'Square Footage', 'Pictures'
        'Property Id', 'URL', 'Auction Start Time', 'Payment Type', 'Listing Agent Info',
        'Event Name', 'Event Details', 'Property Details', 'Listing Information', 'Auction Disclaimers',
        'Price History', 'Tax History', 'Current Market Trends', 'Rental Info']

    address = listing.find(class_="address-line-1").get_text()

    city = listing.find(id="crumb5").get_text()
    
    zip = getZip(str(listing.find(class_="property-address").get_text().replace('\n', '').replace(' ', '')))

    state = listing.find(id="crumb4").get_text()
    #state = state.find("a").get_text()

    strtbid = listing.find(class_="bid-amount").get_text()

    try:
        reservemet = listing.find(class_="event-status failed reverve-not-met")
        reservemet = "No"
    except:
        reservemet = "Yes"

    info = listing.find_all(class_= "first-field bolded")
    proptype = cleanString(info[0].get_text().replace('\n', ''))
    beds = cleanString(info[1].get_text().replace('\n', ''))
    sqft = cleanString(info[3].get_text().replace('\n', ''))
    propid = cleanString(info[4].get_text().replace('\n', ''))

    # TODO: pictures
    # TODO: url

    strttime = listing.find(class_= "event-dates").get_text().replace('\n', '')

    try:
        paytype = listing.find(class_= "cash-only-label")
        paytype = "Cash Only"
    except:
        paytype = "Eligible For Financing"

    csv_writer.writerow(headers)
    csv_writer.writerow([address, city, zip, state, strtbid, 
        reservemet, proptype, beds, sqft, propid, strttime, paytype])

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