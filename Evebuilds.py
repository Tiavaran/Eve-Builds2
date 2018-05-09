import requests
import json
import time
import threading
import _thread
import esipy
from esipy import EsiClient
from esipy import App


def getdata(threadName, delay, shipdict):
    while True:
        r = requests.get('https://redisq.zkillboard.com/listen.php')
        test = r.json()
        try:
            t = test["package"]["killmail"]["victim"]["items"]
            ship = test["package"]["killmail"]["victim"]["ship_type_id"]
            if ship in shipdict:
                shipslots = shipdict.get(ship)
                for x in t:
                    flag = True
                    j = x["item_type_id"]
                    l = x["flag"]
                    if l >= 11 and l < 19:
                      mydict = shipslots[0]
                    elif l >= 19 and l < 26:
                      mydict = shipslots[1]
                    elif l >= 27 and l <= 34:
                      mydict = shipslots[2]
                    elif l >= 92 and l <= 94:
                      mydict = shipslots[3]
                    else:
                      flag = False
                    if (j in mydict) and flag:
                        mydict["count"] = mydict["count"] + 1
                        z = mydict.get(j)
                        mydict[j] = z + 1
                    else:
                        mydict["count"] = mydict["count"] + 1
                        mydict[j] = 1

            else:
                p = 0
                shipdict[ship] = [{}, {}, {}, {}]
                shipslots = shipdict.get(ship)
                flag = True
                for x in t:
                    j = x["item_type_id"]
                    l = x["flag"]
                    if l >= 11 and l <= 18:
                        mydict = shipslots[0]
                    elif l >= 19 and l < 26:
                        mydict = shipslots[1]
                    elif l >= 27 and l <= 34:
                        mydict = shipslots[2]
                    elif l >= 92 and l <= 94:
                        mydict = shipslots[3]
                    else:
                        flag = False
                    if (j in mydict) and flag:
                        mydict["count"] = 1
                        z = mydict.get(j)
                        mydict[j] = z+1
                    elif flag:
                        mydict["count"] = 1
                        mydict[j] = 1



            #print(ship)
            time.sleep(delay)
        except:
            print("Null Package")

try:
    shipdict = {}

    _thread.start_new_thread(getdata, ("Thread-1", 10,shipdict))

except:
    print('Error: unable to start thread')
while 1:
    try:
        test = input("Enter a ship id or print ship list(list): ")
        if test == "list":
            shiptest = shipdict
            for t in shiptest:
                print(t)
        else:
            x = shipdict.get(int(test))
            test = input("Enter Slot type(0-3): ")
            y = x[int(test)]
            for j in y:
                print(j)
    except:
        print("invalid id")

