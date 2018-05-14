import requests
import json
import time
import threading
import _thread
import esipy
from esipy import EsiClient
from esipy import App
import logging


def getdata(threadName, delay, shipdict):
    while True:
        r = requests.get('https://redisq.zkillboard.com/listen.php')
        killmail = r.json()
        try:
            km = killmail["package"]["killmail"]["victim"]["items"]
            ship_id = killmail["package"]["killmail"]["victim"]["ship_type_id"]
            if ship_id in shipdict:
                ship = shipdict.get(ship_id)
                for x in km:
                    flag = True
                    item_id = x["item_type_id"]
                    fnum = x["flag"]
                    if 11 <= fnum <= 18:
                        currslot = ship[0]
                    elif 19 <= fnum <= 26:
                        currslot = ship[1]
                    elif 27 <= fnum <= 34:
                        currslot = ship[2]
                    elif 92 <= fnum <= 94:
                        currslot = ship[3]
                    else:
                      flag = False
                    #Continue if item is one of our tracked slots.
                    if flag:
                        if item_id in currslot:
                            mydict["count"] = mydict["count"] + 1
                            z = mydict.get(ship_id)
                            mydict[ship_id] = z + 1
                        else:
                            mydict["count"] = mydict["count"] + 1
                            mydict[ship_id] = 1
            else:
                shipdict[ship_id] = [{}, {}, {}, {}]
                ship = shipdict.get(ship_id)
                for x in km:
                    flag = True
                    flag = True
                    item_id = x["item_type_id"]
                    fnum = x["flag"]
                    if fnum >= 11 and fnum <= 18:
                        currslot = ship[0]
                    elif fnum >= 19 and fnum < 26:
                        mydict = ship[1]
                    elif fnum >= 27 and fnum <= 34:
                        mydict = ship[2]
                    elif fnum >= 92 and fnum <= 94:
                        mydict = ship[3]
                    else:
                        flag = False
                    if flag:
                        if item_id in mydict:
                            mydict["count"] = mydict["count"] + 1
                            z = mydict.get(item_id)
                            mydict[item_id] = z+1
                        else:
                            if "count" in mydict:
                                mydict["count"] = mydict["count"] + 1
                                mydict[item_id] = 1
                            else:
                                mydict["count"] = 1
                                mydict[item_id] = 1
            #print(ship)
            #print(ship_id)
            time.sleep(delay)
        except Exception as e:
            logging.exception(e)


try:
    shipdict = {}

    _thread.start_new_thread(getdata, ("Thread-1", 10, shipdict))

except:
    print('Error: unable to start thread')
while 1:
    try:
        uinput = input("Enter a ship id or print ship list(list): ")
        if uinput == "list":
            shiplist = shipdict
            for ship_id in shiplist:
                print(ship_id)
        else:
            x = shipdict.get(int(uinput))
            uinput_id = input("Enter Slot type(0-3): ")
            i_list = x[int(uinput_id)]
            for key, values in i_list.items():
                if key == 'count':
                    print("Total count: " + str(values))
                else:
                    divider = i_list["count"]
                    percent = values / divider
                    print(str(key) + ": " + str(percent))
    except:
        print("invalid id")

