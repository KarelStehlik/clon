from imports import *
def a(p):
    print(p)
clock.schedule_once(lambda dt: a("klm"),2)
while True:
    clock.tick()
