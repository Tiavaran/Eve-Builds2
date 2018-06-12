import requests
import json
import time
import threading
from sys import stdout, stderr
import urllib.request
import urllib.parse
import logging
import numpy as np


def print_to_file(shipdict):
    lock.acquire()
    with open('data.json', 'w') as fp:
        fp.truncate()
        json.dump(shipdict, fp, indent=1)
    lock.release()


def auto_write_file(delay, shipdict):
    while 1:
        time.sleep(delay)
        print_to_file(shipdict)
        print_i_cache()

def  print_i_cache():
    lock.acquire()
    with open('item_data.json', 'w') as fp:
        fp.truncate()
        json.dump(name_cache, fp, indent=1)
    lock.release()


def load_icache_from_file():
    with open('item_data.json') as fp:
        data = json.load(fp)
    for key, values in data.items():  # rebuilt the dictionary; needed due to how json stores keys
        # for x in range(0,3):
        name_cache[int(key)] = values


def load_from_file(shipdict):
    with open('data.json') as fp:
        data = json.load(fp)
    for key, values in data.items():  # rebuilt the dictionary; needed due to how json stores keys
        # for x in range(0,3):
        x = data[key]
        shipdict[int(key)] = [{}, {}, {}, {}] # initialize the dict entry for each hull
        for iter in range(0, 4):
            list = x[iter]  # iterate through the loaded data from data.json
            # shipdict[int(key)][iter]["count"] = list["count"]
            for ikey, ivalue in list.items():
                if ikey == "count":
                    shipdict[int(key)][iter][ikey] = ivalue # count is the only key that is a string
                else:
                    shipdict[int(key)][iter][int(ikey)] = ivalue # convert all other keys into integers
    return shipdict


def getdata(delay, shipdict):
    while True:
        r = requests.get('https://redisq.zkillboard.com/listen.php')  # Wait for a kill mail to in then pick it up
        killmail = r.json() # save it in a a json format
        try:
            if killmail is not None:
                km = killmail["package"]["killmail"]["victim"]["items"]  # grab the list of items
                ship_id = killmail["package"]["killmail"]["victim"]["ship_type_id"]   # Grab the item ID of the hull
                lock.acquire()
                # Ship exists in the dict
                if ship_id in shipdict:
                    ship = shipdict.get(ship_id)  # Grab the lists for that ship
                    for x in km:
                        flag = True
                        item_id = x["item_type_id"]
                        fnum = x["flag"]
                        if 11 <= fnum < 19:   # Check which slot the item is in
                            currslot = ship[0]
                        elif 19 <= fnum < 27:
                            currslot = ship[1]
                        elif 27 <= fnum < 35:
                            currslot = ship[2]
                        elif 92 <= fnum < 95:
                            currslot = ship[3]
                        else:
                            flag = False
                        # Continue if item is one of our tracked slots.
                        if flag:
                            # Item exists already
                            if item_id in currslot:  # This item has been seen for this hull previously
                                # Increment total slot count and this item count
                                currslot["count"] = currslot["count"] + 1
                                currslot[item_id] = currslot[item_id] + 1
                                lock.release()
                                # check if this item fits in the top 10 then update the list
                                index = check_top_ten(currslot, currslot[item_id])
                                shift_top_ten(currslot, item_id, index)
                                lock.acquire()
                            else:
                                # Item does not exist
                                if "count" in currslot: # We have seen items for this hull in this slot
                                    # increment the total slot count and initialize this item count to 1
                                    currslot["count"] = currslot["count"] + 1
                                    currslot[item_id] = 1
                                    lock.release()
                                    # Check the top 10 and update if necessary
                                    index = check_top_ten(currslot, currslot[item_id])
                                    shift_top_ten(currslot, item_id, index)
                                    lock.acquire()
                                else:
                                        # if no items have been seen for this hull in this slot initialize the dict
                                    currslot["count"] = 1
                                    currslot[item_id] = 1
                                    # Start the top 10 item list
                                    currslot[1] = item_id
                                    currslot[0] = 0
                                    # initialize the rest of the top 10 to 0
                                    for num in range(2, 11):
                                        currslot[num] = 0
                                    """lock.release()
                                    index = check_top_ten(currslot, currslot[item_id])
                                    shift_top_ten(currslot, item_id, index)
                                lock.acquire()"""

            # Ship does not exist in the dict
            else:
                # initialize the lists of dictionaries for this hull; each entry in the list is a slot type
                shipdict[ship_id] = [{}, {}, {}, {}]
                ship = shipdict.get(ship_id)
                for x in km:
                    flag = True
                    item_id = x["item_type_id"]  # Grab the item Id and the slot flag
                    fnum = x["flag"]
                    if 11 <= fnum < 19:  # Check which slot the item is in
                        currslot = ship[0]
                    elif 19 <= fnum < 27:
                        currslot = ship[1]
                    elif 27 <= fnum < 35:
                        currslot = ship[2]
                    elif 92 <= fnum < 95:
                        currslot = ship[3]
                    else:
                        flag = False
                    if flag:
                        if item_id in currslot:
                            # If the item already exists
                            currslot["count"] = currslot["count"] + 1  # Increment total slot count and item count
                            currslot[item_id] = currslot[item_id] + 1
                            lock.release()
                            index = check_top_ten(currslot, currslot[item_id])
                            shift_top_ten(currslot, item_id, index)
                            lock.acquire()
                        else:
                            if "count" in currslot:
                                currslot["count"] = currslot["count"] + 1
                                currslot[item_id] = 1
                                lock.release()
                                index = check_top_ten(currslot, currslot[item_id])
                                shift_top_ten(currslot, item_id, index)
                                lock.acquire()
                            else:
                                currslot["count"] = 1
                                currslot[item_id] = 1
                                currslot[1] = item_id
                                currslot[0] = 0
                                for num in range(2, 11):
                                    currslot[num] = 0
            # print(ship)
            # print(ship_id)
            lock.release()
            time.sleep(delay)
        except Exception as e:
            logging.exception(e)


def check_top_ten(shipslot, itemcount):
    """Indexes 1-10 in each slot dictionary contains the item id of the item that belongs in that slot
    If not in top 10"""
    try:
        test = shipslot[shipslot[10]]
        if itemcount < shipslot[shipslot[10]]:
            return 0
        else:
            # if greater than slot 1
            if itemcount > shipslot[shipslot[1]]:
                return 1
            elif itemcount > shipslot[shipslot[5]]:   # if in top 5
                for x in range(2, 5):
                    if itemcount > shipslot[shipslot[x]]:
                        return x  # return the slot this item will fit in
            else:  # if in top 10 but not top 5
                for y in range(6, 10):
                    if itemcount > shipslot[shipslot[y]]:
                        return y  # return the slot this item will fit in
    except Exception as e:
        logging.exception(e)
        return 0


#port the list of ships into a list for easier display on the homepage
def pstl():
    lock.acquire()
    rList = []
    for keys, values in shipdict.items():
        rList.append(keys)
    lock.release()
    return rList


#port the top 10 item list into a list for display on the web app
def pitl(Ship_ID, layer):
    lock.acquire()
    rList = []
    itemdict = shipdict[int(Ship_ID)][layer]
    for x in range(0, 11):
        if itemdict[x] != 0:
            rList.append(itemdict[x])
    lock.release()
    return rList


def get_count(hull_id, layer):
    return shipdict[int(hull_id)][layer]["count"]

def check_cache(ids):
    return_array = []
    for item in ids:
        if item not in name_cache:
            id_arr = [item]
            result = esi_get_name(id_arr)
            return_array.append(result[0]['name'])
            name_cache[item] = result[0]['name']
        else:
            return_array.append(name_cache[item])
    return return_array


def esi_get_name(ids):
    """Make an HTTPS request using urllib and /v2/universe/names/
    must be given AN ARRAY OF IDS
    if success return array of json formatted response
    https://github.com/PoHuit/sso-standings/blob/master/standings.py"""
    id_array = ids
    id_array = json.dumps(id_array)
    id_array = id_array.encode('utf-8')
    request = urllib.request.Request('https://esi.tech.ccp.is/v2/universe/names/', id_array)
    try:
        response = urllib.request.urlopen(request)
        if response.status == 200:
            try:
                return json.load(response)
            except json.decoder.JSONDecodeError as e:
                print("json error:  ", e, file=stderr)
        else:
            print("bad response status: ", response.status, file=stderr)
    except urllib.error.URLError as e:
        print("http error: ", e.code, file=stderr)
    print("fetch failed for /v2/universe/names/", file=stderr)
    exit(1)


#calculate the usage percent for each item in the top 10
def calculatepercentages(hull_name, layer):
    lock.acquire()
    rList = []
    items = shipdict[int(hull_name)][layer]
    for x in range(0, 11):
        if items[items[x]] != 0:
            rList.append((items[items[x]] / items["count"]) * 100)
    lock.release()
    return rList

def shift_top_ten(shipslot, item_id, index):
    """ Takes the current shipslot dict, the item ID being inserted, and index at which the ID needs to be replaced
        returns 1 if something is inserted and 0 otherwise"""
    lock.acquire()
    try:
        if index is None:
            lock.release()
            return 0
        elif index < 1 or index > 10:
            lock.release()
            return 0
        else:
            if item_id == shipslot[index]:
                lock.release()
                return 0
            for slot in range(10, index, -1):
                shipslot[slot] = shipslot[slot - 1]
            shipslot[index] = item_id
            lock.release()
            return 1

    except Exception as e:
        lock.release()
        logging.exception(e)

try:
    shipdict = {}
    name_cache = {}
    try:
        shipdict = load_from_file(shipdict)
    except ValueError:
        print("No Data To Load")
    try:
        load_icache_from_file()
    except ValueError:
        print("No Data To Load")
    lock = threading.Lock()  # Initilize a lock
    data_thread = threading.Thread(target=getdata, args=(10, shipdict))  # Function to grab killmail data
    data_thread.daemon = True
    # Auto write our to our data file
    auto_write_thread = threading.Thread(target=auto_write_file, args=(15, shipdict))
    auto_write_thread.daemon = True
    data_thread.start()
    auto_write_thread.start()
except Exception as e:
    print('Error: unable to start thread')
    logging.exception(e)
