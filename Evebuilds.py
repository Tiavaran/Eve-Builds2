import requests
import json
import time
import threading
import esipy
from esipy import EsiClient
from esipy import App
import logging


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
        r = requests.get('https://redisq.zkillboard.com/listen.php')
        killmail = r.json()
        try:
            km = killmail["package"]["killmail"]["victim"]["items"]
            ship_id = killmail["package"]["killmail"]["victim"]["ship_type_id"]
            lock.acquire()
            # Ship exists in the dict
            if ship_id in shipdict:
                ship = shipdict.get(ship_id)
                for x in km:
                    flag = True
                    item_id = x["item_type_id"]
                    fnum = x["flag"]
                    if 11 <= fnum < 19:
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
                    item_id = x["item_type_id"]
                    fnum = x["flag"]
                    if 11 <= fnum < 19:
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
                            currslot["count"] = currslot["count"] + 1
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
    try:
        shipdict = load_from_file(shipdict)
    except ValueError:
        print("No Data To Load")
    lock = threading.Lock()
    data_thread = threading.Thread(target=getdata, args=(10, shipdict))
    data_thread.daemon = True
    auto_write_thread = threading.Thread(target=auto_write_file, args=(3600, shipdict))
    auto_write_thread.daemon = True
    data_thread.start()
    auto_write_thread.start()
except Exception as e:
    print('Error: unable to start thread')
    logging.exception(e)
while 1:
    try:
        uinput = input("Enter a ship id or print ship list(list): ")
        if uinput == "list":
            lock.acquire()
            shiplist = shipdict
            for ship_id in shiplist:
                print(ship_id)
            lock.release()
        elif uinput == "backup":
            write_thread = threading.Thread(target=print_to_file, args=(shipdict,))
            write_thread.start()
        else:
            lock.acquire()
            try:
                jtest = int(uinput)
                x = shipdict[jtest]
            except:
                x = shipdict[uinput]
            shipid = input("Enter Slot type(0-3): ")
            itemlist = x[int(shipid)]
            print(itemlist["count"])
            for index in range(1, 10):
                divider = itemlist["count"]
                value = itemlist[itemlist[index]]
                if value == 0:
                    print(str(index) + ". " + str(itemlist[index]) + " - " + str(value) + "%")
                else:
                    percent = value / divider
                    print(str(index) + ". " + str(itemlist[index]) + " - " + str(percent * 100) + "%")
            """for key, values in itemlist.items():
                if key == 'count':
                    print("Total count: " + str(values))
                else:
                    divider = itemlist["count"]
                    percent = values / divider
                    print(str(key) + ": " + str(percent))"""
            lock.release()
    except Exception as e:
        logging.exception(e)