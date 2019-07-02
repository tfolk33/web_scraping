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
    propId = "n/a"
    propType = "n/a"
    county = "n/a"
    lotSize = "n/a"
    yearBuilt = "n/a"
    mlsNum = "n/a"
    beds = "n/a"
    baths = "n/a"
    sqFt = "n/a"
    stories = "n/a"

    def __init__(self, info):
        if len(info) == 10: #Single Family
            self.propId = cleanString(info[0].get_text())
            self.propType = cleanString(info[2].get_text())
            self.county = cleanString(info[4].get_text())
            self.lotSize = cleanString(info[6].get_text())
            self.yearBuilt = cleanString(info[8].get_text())
            self.mlsNum = cleanString(info[1].get_text())
            self.beds = cleanString(info[3].get_text())
            self.baths = cleanString(info[5].get_text())
            self.sqFt = cleanString(info[7].get_text())
            self.stories = cleanString(info[9].get_text())
        elif len(info) == 5: #Land Property
            self.propId = cleanString(info[0].get_text())
            self.propType = cleanString(info[1].get_text())
            self.county = cleanString(info[2].get_text())
            self.lotSize = cleanString(info[3].get_text())
            self.yearBuilt = cleanString(info[4].get_text())

from requests_html import HTMLSession 
# create an HTML Session object
session = HTMLSession()
# Use the object above to connect to needed webpage
resp = session.get("https://www.xome.com/auctions/1026-Maple-Pekin-IL-61554-312026989")
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
    listingInfoObj = ListingInfo(info)
    
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

    try:
        taxHistory = []
        taxHeaders = []

        taxContainer = listing.find(class_ = 'container-school')
        rowHeaders = taxContainer.find(class_ = 'row row-header')
        taxHeadersTemp = rowHeaders.find_all(class_ = 'span3 col-sm-3 col-xs-3')
        count = 0
        for header in rowHeaders.find_all(class_ = 'span2 col-sm-2 col-xs-2'):
            taxHeaders.append(header.get_text())
            if count < len(taxHeadersTemp):
                taxHeaders.append(taxHeadersTemp[count].get_text())
                count += 1   
        rowData = taxContainer.find(id = 'tax-goes-here')
        for row in rowData.find_all(class_ = 'row row-data'):
            headerCount = 0
            dataCount = 0
            dataString = "n/a"
            dataTemp = row.find_all(class_ = 'span3 col-sm-3')
            for data in row.find_all(class_ = 'span2 col-sm-2'):
                dataString += priceHeaders[headerCount] + ": " + cleanString(data.get_text())
                count += 1
                try:
                    if headerCount < len(dataTemp):
                        dataString += priceHeaders[headerCount] + ": " + cleanString(dataTemp[dataCount].get_text())
                        headerCount += 1
                        dataCount += 1
                except:
                    break   
            taxHistory.append(dataString)
    except:
        taxHistory: "No tax history"    

    #List price
    medianListPrice = listing.find(class_ = 'MedianListPrice-value trend-value').get_text()
    try:
        listing.find(class_ = 'MedianListPrice-icon market-trend-up')
        medianListPrice = medianListPrice + " (trending up)"
    except: 
        try:
            listing.find(class_ = 'MedianListPrice-icon market-trend-down')
            medianListPrice = medianListPrice + " (trending down)"
        except:
            medianListPrice = medianListPrice + " (flat trend)"

    #Sold price
    medianSoldPrice = listing.find(class_ = 'MedianSoldPrice-value trend-value').get_text()
    try:
        listing.find(class_ = 'MedianSoldPrice-icon market-trend-up')
        medianSoldPrice = medianSoldPrice + " (trending up)"
    except: 
        try:
            listing.find(class_ = 'MedianSoldPrice-icon market-trend-down')
            medianSoldPrice = medianSoldPrice + " (trending down)"
        except:
            medianSoldPrice = medianSoldPrice + " (flat trend)"

    #Days on market
    daysOnMarketTag = listing.find(class_ = 'DaysOnMarket-value')
    try:
        daysOnMarketTag.find(class_ = 'DaysOnMarket-icon market-trend-up')
        daysOnMarket = daysOnMarketTag.get_text() + " (trending up)"
    except: 
        try:
            daysOnMarketTag.find(class_ = 'DaysOnMarket-icon market-trend-down')
            daysOnMarket = daysOnMarketTag.get_text() + " (trending down)"
        except:
            daysOnMarket = daysOnMarketTag.get_text() + " (flat trend)"

    #Sales List Price
    salesListPrice = listing.find(class_ = 'SalesListPrice-value trend-value').get_text()
    try:
        listing.find(class_ = 'SalesListPrice-icon market-trend-up')
        salesListPrice = salesListPrice + " (trending up)"
    except: 
        try:
            listing.find(class_ = 'SalesListPrice-icon market-trend-down')
            salesListPrice = salesListPrice + " (trending down)"
        except:
            salesListPrice = salesListPrice + " (flat trend)"        

    csv_writer.writerow(headers)
    csv_writer.writerow([address, city, zip, state, strtBid, 
        reservemet, listingInfoObj.propId, listingInfoObj.propType, 
        listingInfoObj.county, listingInfoObj.lotSize, listingInfoObj.yearBuilt,
        listingInfoObj.mlsNum, listingInfoObj.beds, listingInfoObj.baths,
        listingInfoObj.sqFt, listingInfoObj.stories, strtTime, 
        payType, agentName, agentLicNum, agentPhoneNum, 
        agentBrokerage, agentBrokerageLic, agentManagingBroker, 
        agentManagingBrokerLic, propertyDetials, auctionDisclaimers, priceHistory,
        taxHistory, medianListPrice])

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