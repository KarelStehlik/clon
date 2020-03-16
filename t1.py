from imports import *
import threading
def a(dt):
    print('a')
    
class myThread (threading.Thread):
   def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.e=threading.Event()
   def run(self):
      while True:
          clock.tick()
          time.sleep(0.05)
   def fff(self):
      clock.schedule_once(a,2)

thread1=myThread(1)
thread1.start()
thread1.fff()

while True:
    time.sleep(3)
    thread1.fff()
    print("b")

