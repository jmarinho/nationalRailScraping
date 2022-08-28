import urllib.request
import json
from bs4 import BeautifulSoup
from termcolor import colored

DEBUG = True

src="KGX"
dst="CBG"

hours = ["0800","0900","1000","1100","1200","1300","1400","1500","1600","1700","1800","1900","2000","2100","2200","2300"]#,"2400"]
tracks = [["KGX", "CBG"], ["CBG", "KGX"]]

for track in tracks:
    src = track[0]
    dst = track[1]

    for startTime in hours:

        url = "http://ojp.nationalrail.co.uk/service/timesandfares/{}/{}/today/{}/dep".format(src, dst, startTime)
        print(url)

        fp = urllib.request.urlopen(url)
        data = fp.read()

        mystr = data.decode("utf8")
        fp.close()
        soup = BeautifulSoup(mystr, 'html.parser')

        lista = soup.find_all("script", {"type":"application/json"})

        num_lines = len(lista)

        stats =[]
        for i in range(1,num_lines):
            json_list = json.loads(lista[i].contents[0])
            json_item = json_list["jsonJourneyBreakdown"]

            stats.append({"departure":json_item["departureStationName"],
                       "arrival":json_item["arrivalStationName"],
                       "departureTime":json_item["departureTime"],
                       "arrivalTime":json_item["arrivalTime"],
                       "status":json_item["statusMessage"]})

        #returns the time in minutes since midnight
        def getTime(time: str):
            timeVals = time.split(':')
            #timeVal[0] is hours
            return int(timeVals[0]) * 60 + int(timeVals[1])

        def getDelay(status: str):
            if (status == "cancelled"):
                return float("inf")
            if (status == "disrupted"):
                return float("inf")
            if (status == "on time"):
                return float(0)
            if (status == "delayed"):
                return float(0)
            #when train is delayed the status message has the number of delayed mins as a first word: (<X> mins late)
            try:
                return int(status.split(' ')[0])
            except ValueError:
                import pdb
                pdb.set_trace()
                return 0
            except AttributeError:
               return 0
        for elem in stats:

            if elem["status"] != "on time":
                if (DEBUG):
                    print(colored("status {4} -- from {0} to {1} departure {2}, arrival {3}".format(elem["departure"],
                                                                                                elem["arrival"],
                                                                                                elem["departureTime"],
                                                                                                elem["arrivalTime"],
                                                                                                elem["status"]),"red"))
                elemDepart = getTime(elem["departureTime"])
                elemArrival = getTime(elem["arrivalTime"])
                delay = getDelay(elem["status"])
                lateArrival = getTime(elem["arrivalTime"]) + delay

                for secondElem in stats:
                    secondDepart = getTime(secondElem["departureTime"])
                    secondArrival = getTime(secondElem["arrivalTime"])
                    secondDelay = getDelay(secondElem["status"])

                    if(secondDepart >= elemDepart):
                        abstractSecondDelay = (secondArrival + secondDelay) - elemArrival

                        if(abstractSecondDelay < 0):
                            if(DEBUG):
                                print("train with departure {1}, arrival {2} arrived before".format(secondElem["departure"],
                                                                                                  secondElem["departureTime"],
                                                                                                  secondElem["arrivalTime"],
                                                                                                  secondElem["status"]))
                            delay = 0
                            break

                        if(abstractSecondDelay < delay):
                            if(DEBUG):
                                print("train with departure {1}, sched arrival {2} arrived at {3} ({4})".format(secondElem["departure"],
                                                                                                secondElem[ "departureTime"],
                                                                                                secondElem[ "arrivalTime"],
                                                                                                secondArrival + secondDelay,
                                                                                                secondElem["status"]))

                            delay = abstractSecondDelay

                if (DEBUG):
                    print(" Total delay {} minutes/n".format(delay))
                else:
                    if(delay>=15):
                        print(
                            colored("status {4} -- from {0} to {1} departure {2}, arrival {3}".format(elem["departure"],
                                                                                                      elem["arrival"],
                                                                                                      elem[ "departureTime"],
                                                                                                      elem[ "arrivalTime"],
                                                                                                      elem["status"]), "red"))
                        print(" Total delay {} minutes/n".format(delay))

            else:
                if (DEBUG):
                    print("status {4} -- from {0} to {1} departure {2}, arrival {3}".format(elem["departure"],
                                                                                        elem["arrival"],
                                                                                        elem["departureTime"],
                                                                                        elem["arrivalTime"],
                                                                                        elem["status"]))