import requests
import json
import time
import threading
import _thread
import logging
import esipy
from esipy import EsiClient
from esipy import App


def getdata(thread_name, delay, shipdict):
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
                    if (item_id in currslot) and flag:
                        ship[4] = ship[4] + 1
                        z = currslot.get(item_id)
                        currslot[item_id] = z + 1
                    else:
                        ship[4] = ship[4] + 1
                        currslot[item_id] = 1

            else:
                shipdict[ship_id] = [{}, {}, {}, {}]
                ship = shipdict.get(ship_id)
                flag = True
                for x in km:
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
                    if (item_id in currslot) and flag:
                        ship[4] = ship[4] + 1
                        z = currslot.get(item_id)
                        currslot[item_id] = z+1
                    elif flag:
                        ship[4] = ship[4] + 1
                        currslot[item_id] = 1

            print(ship_id)
            time.sleep(delay)
        except Exception as e:
            logging.exception(e)


try:
    shipdict = {}

    _thread.start_new_thread(getdata, ("Thread-1", 10,shipdict))

except Exception as e:
    logging.exception(e)
while 1:
    test = input("Enter a ship id: ")
    x = shipdict.get(int(test))
    print(x)

