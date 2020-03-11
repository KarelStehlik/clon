#!flask/bin/python
from imports import *
scheduler = BackgroundScheduler()
app = Flask(__name__)
s=0     #s0 s1
players=[]
bullets=[]
gravity=0.65
turn=0
from server_class import *

def ScanDown(x,y,map1):
    r=100000000
    for e in map1:
        if e.x<x and e.x+e.width>x and e.y+e.height<=y:
            r=min(r,y-e.y-e.height)
    return(r)

def tick():
    for e in bullets:
        e.fly()
    global players, map1, gravity
    if shooting:
        if time.time()-players[-1].lastshot>=players[-1].cd:
            players[-1].shoot(0,turn, mousex-players[-1].graphicx, mousey-players[-1].y-players[-1].hitboxh//2)
    for e in players:
        if ScanDown(e.x,e.y,map1):
            e.v-=gravity
        else:
            e.v=max(e.v,0)
        e.y+=max(e.v,-ScanDown(e.x,e.y,map1))
        if e.y<0:
            e.die(0,turn)
            e.v=max(e.v,0)

def run(self):
    global turn
    global camx
    if self.active==0:
        lgg=self.log
        self.hp=self.maxhp
        self.dead=0
        self.x=50
        self.y=300
        if(self.side==1):
            self.x=600
        for e in self.log:
            if e[0]=="S":
                clock.schedule_once(self.shoot,e[1],turn,e[2],e[3])
            if e[0]=="w":
                clock.schedule_once(self.w,e[1],turn)
            if e[0]=="d":
                clock.schedule_once(self.d,e[1],turn)
            if e[0]=="a":
                clock.schedule_once(self.a,e[1],turn)
            if e[0]=="ded":
                clock.schedule_once(self.die,e[1],turn)
            if self.hp<=0:
                break
        self.log=lgg

def Spawn(thing,side):
    global players 
    p1=player()
    p1.t1=time.time()
    for e in players:
        e.active=0
    p1.active=1
    p1.maxhp=thing[0]
    p1.hp=p1.maxhp
    p1.dmg=thing[1]
    p1.cd=thing[2]
    p1.bulletspeed=thing[3]
    p1.rang=thing[4]
    p1.hitboxw=thing[5]
    p1.hitboxh=thing[6]
    p1.walkspeed=thing[7]
    p1.jumppower=thing[8]
    p1.log=[]
    p1.side=side
    if(side==1):
        p1.x=600
        camx=600-place.width/2
    else:
        camx=0
    players.append(p1)
    for e in players:
        run(e)


#scheduler.add_job(tick,'interval',seconds=0.02)

        
    
def NewGame():
    global players, current_map, bullets,gravity,turn,s
    players=[]
    current_map=random.choice(maps)
    bullets=[]
    gravity=0.65
    turn=0
    s=0

NewGame()


@app.route('/GetSide')
def side():
    global s
    if s==0:
        s+=1
        return "0"
    if s==1:
        s=0
        return "1"
    NewGame()
    return "0"



# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)


    
