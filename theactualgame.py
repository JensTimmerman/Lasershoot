import time
import datetime
import MySQLdb
import RPi.GPIO as GPIO
from guizero import App

app = App(bg="green")

db = MySQLdb.connect(host="dlw-hackathon.westeurope.cloudapp.azure.com", user="hackathon",
                     passwd="Delaware.2011", db="hackathon")

#create a cursor for the select
cur = db.cursor()
target = [100000, 801.0, 1784.0, 833.0, 592.0, 244.0, 596.0, 237.0, 601.0, 239.0, 341.0]
result = [True] * 9
percentage = 0.30

diffList = [0.0] * 10

power = 7
buzzer = 23
ir = 21

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

class Game:
    def __init__(self):

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(power,GPIO.OUT)
        GPIO.output(power,GPIO.HIGH)

        GPIO.setup(buzzer,GPIO.OUT)
        GPIO.output(buzzer,GPIO.HIGH)

        GPIO.setup(ir,GPIO.IN)

        f = open('team2.csv', 'a')
        f.write('\n')
        self.lastread = 0
        self.lasttime = time.time()
        self.counter = 0
        self.largenumberseen = False
        self.counterWritten = 0
        self.arr = [0] * 11
        self.is_shot = False


    def run(self):
        while(True):
            newlastread = GPIO.input(ir)
            if newlastread != self.lastread:
                if self.counter > 50000:
                    self.largenumberseen = not self.largenumberseen
                if self.largenumberseen and self.counterWritten < 11:
                    self.arr[self.counterWritten] = self.counter;
                    self.counterWritten = self.counterWritten + 1

                if self.counterWritten == 11:
                    self.counterWritten = 0
                    self.is_shot = compare(self.arr)

                    if self.is_shot:
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

                    print(self.is_shot)
                    self.counter = 0
                    self.largenumberseen = False
                    self.counterWritten = 0
                    self.arr = [0] * 11
                else:

                    self.counter = 0
                    self.lastread = newlastread
                    self.lasttime = time.time()

            else:
                self.counter += 1
