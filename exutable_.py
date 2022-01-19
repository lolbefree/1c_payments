import main
from spammer import spammer
import threading
import os
import multiprocessing


dir_path = os.path.dirname(os.path.realpath(__file__))

from threading import Thread

thread1 = Thread(target=spammer)
# thread2 = Thread(target=prescript)

thread1.start()
# thread2.start()
thread1.join()
# thread2.join()