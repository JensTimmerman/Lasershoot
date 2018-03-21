import time
import datetime
import MySQLdb
import os
import signal
import RPi.GPIO as GPIO
from guizero import App

app = App(bg="green")

db = MySQLdb.connect(host="dlw-hackathon.westeurope.cloudapp.azure.com", user="hackathon",
                     passwd="Delaware.2011", db="hackathon")

#create a cursor for the select
cur = db.cursor()

class Game:
    def __init__(self):
        target = [100000, 801.0, 1784.0, 833.0, 592.0, 244.0, 596.0, 237.0, 601.0, 239.0, 341.0]
        result = [True] * 9
        percentage = 0.30

        diffList = [0.0] * 10
        def compare(arr):

            ok = True
            for i in range(1,9):
                arr[i] = (target[1] / arr[1]) * arr[i]
                diffList[i] = abs(target[i] - arr[i])
                result[i-1] = abs(target[i] - arr[i]) <= percentage * target[i]
                if(not (abs(target[i] - arr[i]) <= percentage * target[i])):
                    ok = False
                    break

            print((arr[1:9]))
            print(diffList)
            print(result)
            print('\n')

            return ok

        power = 7
        buzzer = 23
        ir = 21

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(power,GPIO.OUT)
        GPIO.output(power,GPIO.HIGH)

        GPIO.setup(buzzer,GPIO.OUT)
        GPIO.output(buzzer,GPIO.HIGH)

        GPIO.setup(ir,GPIO.IN)




        f = open('team2.csv', 'a')
        f.write('\n')
        lastread = 0
        lasttime = time.time()
        counter = 0
        largenumberseen = False
        counterWritten = 0
        arr = [0] * 11
        isShot = False

        while(True):
            newlastread = GPIO.input(ir)
            if newlastread != lastread:
                if counter > 50000:
                    largenumberseen = not largenumberseen
                if largenumberseen and counterWritten < 11:
                    arr[counterWritten] = counter;
                    counterWritten = counterWritten + 1

                    #print(str(lastread) + " / " + str(counter))
                    #f.write(str(counter) + '\t')

                if counterWritten == 11:
                    counterWritten = 0
                    isShot = compare(arr)

                    if isShot:
                        app.bg = "red"
                        try:
                            file = open('ReadIR/currentGame.txt','r')
                            newId = file.read()
                            print(newId)
                            file.close()
                            file = open('piid','r')
                            piid = file.read()
                            file.close()
                            ts = time.time()
                            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            cur.execute("""INSERT INTO hackathon.scores (game, timestamp, idpi) VALUES (%s, %s, %s)""",
                                        (newId, timestamp, piid))
                            db.commit()
                        except Exception as e:
                            print("error: ", str(e))
                            db.rollback()
                        print('I\'ve been shot! Inactive for 10 seconds!');
                        time.sleep(10);
                        print('I am active! Please, don\'t shoot me, I\'m only the Pi(ano player)!');
                    app.bg = "green"

                    print(isShot)
                    counter = 0
                    largenumberseen = False
                    counterWritten = 0
                    arr = [0] * 11
                else:

                    counter = 0
                    lastread = newlastread
                    newlasttime = time.time()
                    diff = (newlasttime - lasttime)*1000
                #if diff > 5.5 and diff < 6.5:
                #print((newlasttime-lasttime)*1000)
                    lasttime = newlasttime

            else:
                counter = counter + 1
