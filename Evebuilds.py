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

def load_from_file(shipdict):
    with open('data.json') as fp:
        data = json.load(fp)
    return data

def getdata(delay, shipdict):
    while True:
        r = requests.get('https://redisq.zkillboard.com/listen.php')
        killmail = r.json()
        try:
            km = killmail["package"]["killmail"]["victim"]["items"]
            ship_id = killmail["package"]["killmail"]["victim"]["ship_type_id"]
            lock.acquire()
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
                    #Continue if item is one of our tracked slots.
                    if flag:
                        if item_id in currslot:
                            currslot["count"] = currslot["count"] + 1
                            currslot[item_id] = currslot[item_id] + 1
                            check_top_ten(currslot, currslot[item_id])
                        else:
                            if "count" in currslot:
                                currslot["count"] = currslot["count"] + 1
                                currslot[item_id] = 1
                                check_top_ten(currslot, currslot[item_id])
                            else:
                                currslot["count"] = 1
                                check_top_ten(currslot, currslot[item_id])
                                currslot[item_id] = 1
            else:
                shipdict[ship_id] = [{}, {}, {}, {}]
                ship = shipdict.get(ship_id)
                for x in km:
                    flag = True
                    flag = True
                    item_id = x["item_type_id"]
                    fnum = x["flag"]
                    if fnum >= 11 and fnum < 19:
                        currslot = ship[0]
                    elif fnum >= 19 and fnum < 27:
                        currslot = ship[1]
                    elif fnum >= 27 and fnum < 35:
                        currslot = ship[2]
                    elif fnum >= 92 and fnum < 95:
                        currslot = ship[3]
                    else:
                        flag = False
                    if flag:
                        if item_id in currslot:
                            currslot["count"] = currslot["count"] + 1
                            currslot[item_id] = currslot[item_id] + 1
                            check_top_ten(currslot, currslot[item_id])
                        else:
                            if "count" in currslot:
                                currslot["count"] = currslot["count"] + 1
                                currslot[item_id] = 1
                                check_top_ten(currslot, currslot[item_id])
                            else:
                                currslot["count"] = 1
                                currslot[item_id] = 1
                                currslot[1] = item_id
                                for num in range(2, 11):
                                    currslot[num] = 0
            #print(ship)
            #print(ship_id)
            lock.release()
            time.sleep(delay)
        except Exception as e:
            logging.exception(e)

def check_top_ten(shipslot, itemcount):
    #Indexes 1-10 in each slot dictionary contains the item id of the item that belongs in that slot
    numone = shipslot[10]
    if itemcount < shipslot[shipslot[10]]:
        return 0
    else:
        if itemcount > shipslot[shipslot[1]]:
            return 1
        elif itemcount > shipdict[shipslot[5]]:
            for x in range(2, 5):
                if itemcount > shipslot[shipslot[x]]:
                    return x
        else:
            for y in range(6, 10):
                if itemcount > shipslot[shipslot[y]]:
                    return y

try:
    shipdict = {}
    try:
        shipdict = load_from_file(shipdict)
    except:
        print("No Data To Load")
    lock = threading.Lock()
    data_thread = threading.Thread(target=getdata, args=(10, shipdict))
    data_thread.daemon = True
    data_thread.start()
except:
    print('Error: unable to start thread')
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
            x = shipdict.get(int(uinput))
            shipid = input("Enter Slot type(0-3): ")
            itemlist = x[int(shipid)]
            for key, values in itemlist.items():
                if key == 'count':
                    print("Total count: " + str(values))
                else:
                    divider = itemlist["count"]
                    percent = values / divider
                    print(str(key) + ": " + str(percent))
            lock.release()
    except Exception as e:
        logging.exception(e)