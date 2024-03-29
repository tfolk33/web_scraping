from bs4 import BeautifulSoup
from csv import writer

import time
import csv
import sqlite3
import re
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests_html import HTMLSession

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

def getInfo(listing, csv_writer, url):
    address = listing.find(class_="address-line-1").get_text()

    city = listing.find(id="crumb5").get_text()
    
    zip = getZip(str(listing.find(class_="property-address").get_text().replace('\n', '').replace(' ', '')))

    state = listing.find(id="crumb4").get_text()
    #state = state.find("a").get_text()

    strtBid = listing.find(class_="bid-amount").get_text()

    try:
        reserveMet = listing.find(class_="event-status failed reverve-not-met")
        reserveMet = "No"
    except:
        reserveMet = "Yes"

    reservePrice = listing.find(class_ = "reserve-price")
    if reservePrice != None:
        reservePrice = reservePrice.get_text()
    else:
        reservePrice = "Not Disclosed"

    info = listing.find_all(class_= "listing-value")
    listingInfoObj = ListingInfo(info)
    
    # TODO: pictures
    pictureURLs = []
    pictureSlides = listing.find(class_ = "slides")
    if pictureSlides != None:
        pictures = pictureSlides.find_all('img')
        for picture in pictures:
            pictureURLs.append(picture['src'])
    else:
        pictureURLs = "No Pictures Found"        
    
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
    agentName = "n/a"
    agentLicNum ="n/a"
    agentPhoneNum = "n/a"
    agentBrokerage = "n/a"
    agentBrokerageLic = "n/a"
    agentManagingBroker = "n/a"
    agentManagingBrokerLic = "n/a"
    agentEmail = "n/a"

    agentTable = listing.find_all('table', attrs={'class':'pd-table table-striped'})
    if len(agentTable) > 0:
        try:
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
        except:
            print("End of agent info: length - " + str(len(agentTable)))

        agentEmail = listing.find(class_="xmicon icon-email").get_text()

    eventName = listing.find(id = "eventName")

    #TODO: event detials - could be the same as start time
    eventDetails = "Coming Soon.."

    propertyDetials = listing.find(class_ = "property-content").get_text().replace('\n', '')

    auctionDisclaimers = []
    ulAuctDisclaimers = listing.find(id = "ulAuctionDisclaimer")
    for li in ulAuctDisclaimers.find_all('li'):
        auctionDisclaimers.append(li.get_text())

    #TODO: fix price and tax history
    # So looks like the Handlebars Template is not being loaded when the page is so its not happy
    # Also could be any number of things so we'll see
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


    # browser = webdriver.Chrome()
    # browser.get("https://www.xome.com/auctions/222-28-Edmore-Ave-Queens-Village-NY-11428-313115854")
    # time.sleep(1)
    
    try:
        taxHistory = []
        taxHeaders = []

        taxContainer = browser.find_element_by_class_name('container-school')
        rowHeaders = browser.find_element_by_class_name('row row-header')
        taxHeadersTemp = browser.find_element_by_class_name('span3 col-sm-3 col-xs-3')
        count = 0
        for header in rowHeaders.find_elements_by_class_name('span2 col-sm-2 col-xs-2'):
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

    
    #TODO: Fix Market trends
    # Beleive it to be a script problem
    # It has worked randomly but almost always doesnt work

    #List price
    medianListPrice = listing.find(class_ = 'MedianListPrice-value trend-value').get_text()
    if listing.find(class_ = 'MedianListPrice-icon market-trend-up') != None:
        medianListPrice = medianListPrice + " (trending up)"
    elif listing.find(class_ = 'MedianListPrice-icon market-trend-down') != None:
        medianListPrice = medianListPrice + " (trending down)"
    else:
        medianListPrice = medianListPrice + " (flat trend)"

    #Sold price
    medianSoldPrice = listing.find(class_ = 'MedianSoldPrice-value trend-value').get_text()
    if listing.find(class_ = 'MedianSoldPrice-icon market-trend-up') != None:
        medianSoldPrice = medianSoldPrice + " (trending up)"
    elif listing.find(class_ = 'MedianSoldPrice-icon market-trend-down') != None:
        medianSoldPrice = medianSoldPrice + " (trending down)"
    else:
        medianSoldPrice = medianSoldPrice + " (flat trend)"

    #Days on market
    daysOnMarketTag = listing.find(class_ = 'DaysOnMarket-value')
    if daysOnMarketTag.find(class_ = 'DaysOnMarket-icon market-trend-up') != None:
        daysOnMarket = daysOnMarketTag.get_text() + " (trending up)"
    elif daysOnMarketTag.find(class_ = 'DaysOnMarket-icon market-trend-down') != None:
        daysOnMarket = daysOnMarketTag.get_text() + " (trending down)"
    else:
        daysOnMarket = daysOnMarketTag.get_text() + " (flat trend)"

    #Sales List Price
    salesListPrice = listing.find(class_ = 'SalesListPrice-value trend-value').get_text()
    if listing.find(class_ = 'SalesListPrice-icon market-trend-up') != None:
        salesListPrice = salesListPrice + " (trending up)"
    elif listing.find(class_ = 'SalesListPrice-icon market-trend-down') != None:
        salesListPrice = salesListPrice + " (trending down)"
    else:
         salesListPrice = salesListPrice + " (flat trend)"


    avgHighRent = "n/a"
    avgLowRent = "n/a"
    avgMedianRent = "n/a"

    rentInfoTable = listing.find_all('table', attrs={'class':'table-style'})
    if len(rentInfoTable) > 0:
        rentInfoBody = rentInfoTable[0].find('tbody')

        rows = rentInfoBody.find_all('tr')
        cols = rows[0].find_all('td')
        avgHighRent = cols[1].text.strip()

        cols = rows[1].find_all('td')
        avgMedianRent = cols[1].text.strip()

        cols = rows[2].find_all('td')
        avgLowRent = cols[1].text.strip()

    csv_writer.writerow([address, city, zip, state, strtBid, 
        reserveMet, reservePrice, listingInfoObj.propId, listingInfoObj.propType, listingInfoObj.county,
        listingInfoObj.lotSize, listingInfoObj.yearBuilt, listingInfoObj.mlsNum, listingInfoObj.beds, listingInfoObj.baths,
        listingInfoObj.sqFt, listingInfoObj.stories, pictureURLs, url, strtTime, 
        payType, agentName, agentLicNum, agentPhoneNum, agentBrokerage,
        agentBrokerageLic, agentManagingBroker, agentManagingBrokerLic, eventName, eventDetails,
        propertyDetials, auctionDisclaimers, priceHistory, taxHistory, medianListPrice,
        medianSoldPrice, daysOnMarket, salesListPrice, avgHighRent, avgLowRent,
        avgMedianRent])

    print("Added a new property")

####################################################

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

#####################################################################

# # create an HTML Session object
session = HTMLSession()
# Use the object above to connect to needed webpage
resp = session.get("https://www.xome.com/auctions/bank-owned")
# Run JavaScript code on webpage
resp.html.render(timeout=480)

homePage = BeautifulSoup(resp.html.html, 'html.parser')
time.sleep(5)
pg = 1
totalPgs = float(homePage.find(class_ = "results-counter-number").get_text().replace(',', '')) / 20 + 1
listing_links = []
browser = webdriver.Chrome()
while(pg < 2):
    browser.get("https://www.xome.com/auctions/bank-owned?page=" + str(pg))
    time.sleep(2)
    listings = browser.find_elements_by_xpath("//a[@class='property-detail-link']")
    
    if len(listings) < 20:
        print("oops")

    for listing in listings:
        listing_links.append(listing.get_attribute('href'))

    pg += 1            

with open('properties.csv', 'w') as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Address', 'City', 'Zip Code', 'State', 'Starting Bid', 
        'Reserve Met', 'Reserve Price', 'Property Id', 'Property Type', 'County',
        'Lot Size', 'Year Built', 'MLS#', 'Bedrooms', 'Bathrooms', 'Square Feet', 'Stories', 'Pictures',
        'URL', 'Auction Start Time', 'Payment Type', 'Listing Agent Name', 'Listing Agent License Number',
        'Listing Agent Phone Number', 'Listing Agent Brokerage', 'Listing Agent Brokerage License',
        'Managing Broker Name', 'Managing Broker License', 'Event Name',
        'Event Details', 'Property Details', 'Auction Disclaimers',
        'Price History', 'Tax History', 'Medan List Price', 'Median Sold Price', 'Days On Market',
        'Sales List Price', 'Average High Rent', 'Average Median Rent', 'Average Low Rent']
    csv_writer.writerow(headers)

    count = 0
    for listing in listing_links:
        session = HTMLSession()
        # Use the object above to connect to needed webpage
        print("Connecting to listing")
        resp = session.get(listing)
        # Run JavaScript code on webpage
        print("Rendering")
        resp.html.render(timeout=10)
        listingSoup = BeautifulSoup(resp.html.html, 'html.parser')
        print("Processing a new property")
        getInfo(listingSoup, csv_writer, listing)
        if (count > 1):
            break
        count += 1

#Tansfer to SQL db
con = sqlite3.connect("PropertyData.db")
cur = con.cursor()
cur.execute("DROP TABLE Properties")
cur.execute("CREATE TABLE IF NOT EXISTS Properties ('Address', 'City', 'Zip_Code', 'State', 'Starting_Bid', 'Reserve_Met', 'Reserve_Price', 'Property_Id', 'Property_Type', 'County', 'Lot_Size', 'Year_Built', 'MLS_Number', 'Bedrooms', 'Bathrooms', 'Square_Feet', 'Stories', 'Pictures', 'URL', 'Auction_Start_Time', 'Payment_Type', 'Listing_Agent_Name', 'Listing_Agent_License_Number', 'Listing_Agent_Phone_Number', 'Listing_Agent_Brokerage', 'Listing_Agent_Brokerage_License_Number', 'Managing_Broker_Name', 'Managing_Broker_License', 'Event_Name', 'Event_Details', 'Property_Details', 'Auction_Disclaimers', 'Price_History', 'Tax_History', 'Median_List_Price', 'Median_Sold_Price', 'Days_On_Market','Sales_List_Price', 'Average_High_Rent', 'Average_Median_Rent', 'Average_Low_Rent');") 
       # use your column names here

with open('properties.csv','rt') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['Address'], i['City'], i['Zip Code'], i['State'], i['Starting Bid'], 
       i['Reserve Met'], i['Reserve Price'], i['Property Id'], i['Property Type'], i['County'],
       i['Lot Size'], i['Year Built'], i['MLS#'], i['Bedrooms'], i['Bathrooms'], i['Square Feet'],
       i['Stories'], i['Pictures'], i['URL'], i['Auction Start Time'], i['Payment Type'],
       i['Listing Agent Name'], i['Listing Agent License Number'], i['Listing Agent Phone Number'],
       i['Listing Agent Brokerage'], i['Listing Agent Brokerage License'], i['Managing Broker Name'],
       i['Managing Broker License'], i['Event Name'], i['Event Details'], i['Property Details'], 
       i['Auction Disclaimers'], i['Price History'], i['Tax History'],
       i['Medan List Price'], i['Median Sold Price'], i['Days On Market'],i['Sales List Price'],
       i['Average High Rent'], i['Average Median Rent'], i['Average Low Rent']) for i in dr]

cur.executemany("INSERT INTO Properties (Address, City, Zip_Code, State, Starting_Bid, Reserve_Met, Reserve_Price, Property_Id, Property_Type, County, Lot_Size, Year_Built, MLS_Number, Bedrooms, Bathrooms, Square_Feet, Stories, Pictures, URL, Auction_Start_Time, Payment_Type, Listing_Agent_Name, Listing_Agent_License_Number, Listing_Agent_Phone_Number, Listing_Agent_Brokerage, Listing_Agent_Brokerage_License_Number, Managing_Broker_Name, Managing_Broker_License, Event_Name, Event_Details, Property_Details, Auction_Disclaimers, Price_History, Tax_History, Median_List_Price, Median_Sold_Price, Days_On_Market, Sales_List_Price, Average_High_Rent, Average_Median_Rent, Average_Low_Rent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?);", to_db)
con.commit()
con.close()