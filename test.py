import time
from threading import Thread

import schedule


def w1():
    while 1:
        print("aaaaaa")
        time.sleep(5)


def job():
    print('job')


schedule.every(10).seconds.do(job)


def w3():
    while True:
        schedule.run_pending()


thread1 = Thread(target=w1)
thread2 = Thread(target=w3)

thread1.start()
thread2.start()
thread1.join()
thread2.join()
