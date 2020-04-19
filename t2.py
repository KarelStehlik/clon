from imports import *
a=0
def tick():
    global a
    a+=1
class TickThread(threading.Thread):
    def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = threadID
    def run(self):
        clock.schedule_interval(lambda dt: tick(),1/60)
        while True:
            time.sleep(1/100)
            clock.tick()
tt=TickThread(1)
tt.start()
