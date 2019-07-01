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

def scroll():
    scroll_delay = 15
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Action scroll down
        # elem.send_keys(Keys.END)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_delay)
        new_height = browser.execute_script("return document.body.scrollHeight")
            
        if new_height == last_height:
            break
        last_height = new_height

def cleanString(input):
    count = 0
    for letter in str(input):
        if letter.isspace():
            count += 1
        else:
            break
    input = str(input[count:])
    revinp = reversed(input)
    count = 0
    for letter in revinp:
        if letter.isspace():
            count += 1
        else:
            break
    if count != 0:        
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
# for post in post_elems:
#    print(post.text)

#############################################

class ListingInfo:
    propId = "not found"
    propType = "not found"
    county = "not found"
    lotSize = "not found"
    yearBuilt = "not found"
    mlsNum = "not found"
    beds = "not found"
    baths = "not found"
    sqFt = "not found"
    stories = "not found"

    def __init__(self, propId, mlsNum, propType, beds, county, baths, lotSize, sqFt, yearBuilt, stories):
        self.propId = propId
        self.propType = propType
        self.county = county
        self.lotSize = lotSize
        self.yearBuilt = yearBuilt
        self.mlsNum = mlsNum
        self.beds = beds
        self.baths = baths
        self.sqFt = sqFt
        self.stories = stories

from requests_html import HTMLSession 
# create an HTML Session object
session = HTMLSession()
# Use the object above to connect to needed webpage
resp = session.get("https://www.xome.com/auctions/18-7855-Ewalina-Road-Mountain-View-HI-96771-303717185")
# Run JavaScript code on webpage
resp.html.render(timeout=480)

import csv
import sqlite3
import re

listing = BeautifulSoup(resp.html.html, 'html.parser')

with open('properties.csv', 'w') as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Address', 'City', 'Zip Code', 'State', 'Starting Bid', 
        'Reserve Met', 'Resreve Price', 'Property Id', 'Property Type', 'County',
        'Lot Size', 'Year Built', 'MLS#', 'Bedrooms', 'Bathrooms', 'Square Feet', 'Stories', 'Pictures'
        'URL', 'Auction Start Time', 'Payment Type', 'Listing Agent Name', 'Listing Agent License Number',
        'Listing Agent Phone Number', 'Listing Agent Brokerage', 'Listing Agent Brokerage License',
        'Managing Broker Name', 'Managing Broker License'
        'Event Name', 'Event Details', 'Property Details', 'Listing Information', 'Auction Disclaimers',
        'Price History', 'Tax History', 'Current Market Trends', 'Rental Info']

    address = listing.find(class_="address-line-1").get_text()

    city = listing.find(id="crumb5").get_text()
    
    zip = getZip(str(listing.find(class_="property-address").get_text().replace('\n', '').replace(' ', '')))

    state = listing.find(id="crumb4").get_text()
    #state = state.find("a").get_text()

    strtBid = listing.find(class_="bid-amount").get_text()

    try:
        reservemet = listing.find(class_="event-status failed reverve-not-met")
        reservemet = "No"
    except:
        reservemet = "Yes"

    info = listing.find_all(class_= "listing-value")
    listingInfoObj = ListingInfo(cleanString(info[0].get_text()), cleanString(info[1].get_text()), 
    cleanString(info[2].get_text()), cleanString(info[3].get_text()),
    cleanString(info[4].get_text()), cleanString(info[5].get_text()),
    cleanString(info[6].get_text()), cleanString(info[7].get_text()),
    cleanString(info[8].get_text()), cleanString(info[9].get_text()))
    
    # TODO: pictures
    # TODO: url

    strtTime = listing.find(class_= "event-dates").get_text().replace('\n', '')

    try:
        payType = listing.find(class_= "cash-only-label")
        payType = "Cash Only"
    except:
        try:
            payType = listing.find(Class_="icon-finance")
            payType = "Eligible For Financing"
        except:
            payType = "Payment Type Not Recognized"

    #Listing Agent Info: Name, License #, Phone, etc
    agentTable = listing.find_all('table', attrs={'class':'pd-table table-striped'})
    agentBody = agentTable[0].find('tbody')

    rows = agentBody.find_all('tr')
    cols = rows[0].find_all('td')
    agentName = cols[1].text.strip()

    cols = rows[1].find_all('td')
    agentLicNum = cols[1].text.strip()

    cols = rows[2].find_all('td')
    agentPhoneNum = cols[1].text.strip()

    cols = rows[3].find_all('td')
    agentBrokerage = cols[1].text.strip()

    cols = rows[4].find_all('td')
    agentBrokerageLic = cols[1].text.strip()

    cols = rows[5].find_all('td')
    agentManagingBroker = cols[1].text.strip()

    cols = rows[6].find_all('td')
    agentManagingBrokerLic = cols[1].text.strip()

    agentEmail = listing.find(class_="xmicon icon-email").get_text()

    eventName = listing.find(id = "eventName")

    #TODO: event detials - could be the same as start time

    propertyDetials = listing.find(class_ = "property-content").get_text().replace('\n', '')

    auctionDisclaimers = []
    ulAuctDisclaimers = listing.find(id = "ulAuctionDisclaimer")
    for li in ulAuctDisclaimers.find_all('li'):
        auctionDisclaimers.append(li.get_text())

    try:
        priceHistory = []
        priceHeaders = []

        priceContainer = listing.find(class_ = 'container-price-history')
        rowHeaders = priceContainer.find(class_ = 'row row-header')
        for header in rowHeaders.find_all(class_ = 'span3 col-sm-3 col-xs-3'):
            priceHeaders.append(header.get_text())
        rowData = priceContainer.find(id = 'price-goes-here')
        for row in rowData.find_all(class_ = 'row row-data'):
            count = 0
            dataString = "n/a"
            for data in row.find_all(class_ = 'span3 col-sm-3'):
                dataString += priceHeaders[count] + ": " + cleanString(data.get_text())
                count += 1
            priceHistory.append(dataString)
    except:
        priceHistory: "No price history"


    csv_writer.writerow(headers)
    csv_writer.writerow([address, city, zip, state, strtBid, 
        reservemet, listingInfoObj.propId, listingInfoObj.propType, 
        listingInfoObj.county, listingInfoObj.lotSize, listingInfoObj.yearBuilt,
        listingInfoObj.mlsNum, listingInfoObj.beds, listingInfoObj.baths,
        listingInfoObj.sqFt, listingInfoObj.stories, strtTime, 
        payType, agentName, agentLicNum, agentPhoneNum, 
        agentBrokerage, agentBrokerageLic, agentManagingBroker, 
        agentManagingBrokerLic, propertyDetials, auctionDisclaimers])

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