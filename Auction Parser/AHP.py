import re
import time
import cv2
import threading as th

# Globals
exportFileName = ""
iniFileName = ""
doExecute = True

import os	
clear = lambda: os.system('cls')	# Clear Console


# File Input and Data Parse
def getMarketValues():
	
	print("[SysNote]  Parsing AppData.lua")
	filepath = "C:\Program Files (x86)\World of Warcraft\_classic_\Interface\AddOns\TradeSkillMaster_AppHelper\AppData.lua"

	file = open(filepath, 'r')

	lines = []

	for line in file:
		lines.append(line)
	
	file.close()
	
	print("[SysNote]  Parsing Complete")
	return lines[1]


# Create Item to add to search
def createItemInstance():
	
	itemID = input("Enter Item ID: ")
	itemName = input("Enter Item Name: ")
	
	return (itemID, itemName)

# Parameter Version
def createItemInstancePara(itemID, itemName):
	
	#itemID = input("Enter Item ID: ")
	#itemName = input("Enter Item Name: ")
	
	return (itemID, itemName)

# Create regex string and search the AH, and return the auction data for the hour
def searchAuctionData(itemID, marketData):
	
	itemSearchData = []
	
	itemSearchRegex = itemID[0] + "\,\d+\,\d+\,\d+\,\d+" # Generate Regex for itemID
	#print(itemSearchRegex)
	
	itemSearchLuaString = re.findall(itemSearchRegex, marketData)

	itemSearchLuaString = itemSearchLuaString[0]
	timeStamp = time.localtime()
		
	itemSearchData.append(timeStamp[0]) # Year
	itemSearchData.append(timeStamp[1]) # Month
	itemSearchData.append(timeStamp[2]) # Day (Date)
	itemSearchData.append(timeStamp[3]) # Hour
	itemSearchData.append(timeStamp[6]) # Day (Weekday)

	itemSearchTempString = itemSearchLuaString.split(',') # String format: itemID, marketValue, minbuyout, historical, numAuctions
	#print(itemSearchTempString)
	itemSearchData.append(itemSearchTempString[0]) #itemID, maybe just do a string. will need to rewrite more cleverly so i can add items through a function
	itemSearchData.append(itemID[1]) # Item Name
	itemSearchData.append(int(itemSearchTempString[2])) #minBuyout
	itemSearchData.append(itemSearchTempString[-1]) # num of auctions, might do something with this data.
	
	return tuple(itemSearchData)

def loadIniFile():
	
	#filepath = "C:\\Users\\Christian\\Documents\\Auction Parser\\setup.ini"
	global iniFileName
	filepath = "C:\\Users\\Christian\\Documents\\Auction Parser\\" + iniFileName + ".ini"
	header = "Year, Month, Date, Hour, Weekday, Item ID, Item Name, Min. Buyout, Number of Auctions\n"
	
	file = open(filepath, 'r')
	
	lines = []
	
	for line in file:
		if line[0] == '#': # Skip comment lines
			continue
		elif line[0] == 'f':	# Get filename
			global exportFileName
			exportFileName = line[2:-1]
		elif line[0] == 'i': # Read item lines
			lines.append(tuple(line[2:-1].split(','))) # Return item as a (itemID, itemName) tuple
		
	file.close()
	
	# Make csv file with header
	filepath = "C:\\Users\\Christian\\Documents\\Auction Parser\\" + exportFileName + ".csv"
	
	file = open(filepath, 'w+')
	file.write(header)
		
	file.close()
	
	return lines

def validateItemIDs(itemsToWatch, marketData):
	
	validItemIDs = []
	
	for item in itemsToWatch:
		invalidItem = (None, None)
		itemSearchRegex = item[0] + "\,\d+\,\d+\,\d+\,\d+" 
		
		itemSearchValue = re.search(itemSearchRegex, marketData)
		if itemSearchValue != None:
			validItemIDs.append(item)
		else:
			print("[WARNING]  Item Not Found: " + item[0] + item[1])
			
	return validItemIDs

	
def writeToFile(dataSet):
	
	csvEntries = []
	for item in dataSet:
		if (item != None):
			csvEntries.append(str(item[0]) + ',' + str(item[1]) + ',' + str(item[2]) + ',' + str(item[3]) + ',' + str(item[4]) + ',' + str(item[5]) + ",\"" + str(item[6][1:]) + "\"," + str(item[7])+ "," + str(item[8]))
		else:
			continue
		
	#print(csvEntries)
	
	filepath = "C:\\Users\\Christian\\Documents\\Auction Parser\\" + exportFileName + ".csv"
	
	file = open(filepath, 'a')
	
	for entry in csvEntries:
		lineToWrite = entry + '\n'
		file.write(lineToWrite)
	
	file.close()
	
	
def key_capture_thread():
	global doExecute
	input()
	doExecute = False
	
	
def main():
	
	itemListFile = input("Enter the file name of the .ini with the items to monitor: ")
	global iniFileName
	iniFileName = itemListFile
	clear()
	
	print("[SysNote]  Monitoring items in: " + itemListFile + ".ini")
	
	marketData = getMarketValues()
	
	print("[SysNote]  Waiting... Press \'q\' to exit." )
	
	itemsToWatch = validateItemIDs(loadIniFile(), marketData)
	
	th.Thread(target=key_capture_thread, args = (), name='key_capture_thread', daemon=True).start()
	
	while (doExecute):
		
		dataSet = []
		
		queryTime = time.localtime() # Update CSV at a quarter past every hour
		
		# Fix minute format
		minuteFix = str(queryTime[4])
		if (len(minuteFix) == 1):
			minuteFix = '0' + str(queryTime[4])
		
		waitDelay = (60 - queryTime[5])

		#if (queryTime[4]): # Debugging
		if (queryTime[4] == 0):
			print("[SysNote]  Beginning AuctionDB Update")
			marketData = getMarketValues() # Update Market Values
			
			for item in itemsToWatch:
				if (item != None):
					#print(item)
					print("[Updated] " + item[1] + " at " + str(queryTime[1]) + "/" + str(queryTime[2]) + "/" + str(queryTime[0]) + " " + str(queryTime[3] % 12) + ":" + minuteFix)
					dataSet.append(searchAuctionData(item, marketData))
				else:
					continue
			
			writeToFile(dataSet)
			print("[SysNote]  Waiting... Press \'q\' to exit. Next update at: " + str(queryTime[3]) + ":00")
			while (doExecute) and (waitDelay >= 1):
				time.sleep(1)
				waitDelay -= 1
				
		
			
	
main()
	