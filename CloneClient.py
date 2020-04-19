from imports import *
from client_class import *
scheduler = BackgroundScheduler()
scheduler.start()
place = pyglet.window.Window(resizable=True,caption='CLOWN WARS!')
keys = key.KeyStateHandler()
place.set_minimum_size(100,100)
pyglet.gl.glClearColor(0.2,0.3,1,1)
camx=0
gravity=0.65
turn=0
player_side=int(requests.get("http://localhost:5000/GetSide").text)
mouseheld=False
mousex=0
mousey=0

def run(self):
    global turn
    global camx
    if self.active==0:
        lgg=self.log
        self.hp=self.maxhp
        self.dead=0
        self.x=50
        self.y=300
        self.hpgreen_width=self.hitboxw
        if(self.side==1):
            self.x=600
        for e in self.log:
            if e[0]=="S":
                clock.schedule_once(self.shoot,e[1],turn,e[2],e[3])
            if e[0]=="w":
                clock.schedule_once(self.w,e[1],turn)
                #scheduler.add_job(self.w,'interval',args=[e[1],turn],seconds=e[1],max_instances=1)
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
    global camx
    camx=0
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
    p1.skin=thing[7]
    p1.sk=thing[8]
    p1.walkspeed=thing[9]
    p1.jumppower=thing[10]
    p1.log=[]
    p1.side=side
    p1.hpgreen_width=p1.hitboxw
    p1.hpgreen.width=p1.hitboxw
    p1.hpred.width=p1.hitboxw
    p1.hpred_width=p1.hitboxw
    if(side==1):
        p1.x=600
        camx=600-place.width/2
        p1.skin=thing[11]
        p1.sk=thing[12]
    else:
        camx=0
    players.append(p1)
    players[-1].hpgreen.width=players[-1].hitboxw
    for e in players:
        run(e)

Spawn(BasicGuy,0)
                    
@place.event
def on_mouse_motion(x, y, dx, dy):
    global mousex
    global mousey
    global CCpics,camx
    mousex=x+dx
    mousey=y+dy
    if len(CCpics)>1:
        if mousex<40:
            camx-=2
            for e in CCpics:
                e[1]+=2
        if mousex>place.width-40:
            camx+=2
            for e in CCpics:
                e[1]-=2

@place.event
def on_mouse_press(x, y, button, modifiers):
    global mouseheld
    global turn,CCpics
    mouseheld=True
    if len(CCpics)>1:
        if mousey>20 and mousey<450:
            #i*290+20
            if (mousex+camx)-290*((mousex+camx)//290)>=20 and (mousex+camx)<=290*len(possible_units):
                clone_choice=possible_units[mousex//290]
            
                tick(0)    
                players[-1].die(0,turn)
                turn+=1
                Spawn(clone_choice,player_side)
                for e in bullets:
                    e.die()
                CCpics=[]
    
@place.event
def on_mouse_release(x, y, button, modifiers):
    global mouseheld
    mouseheld=False

@place.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global mousex
    global mousey
    mousex=x+dx
    mousey=y+dy
 


def tick(dt):
    global players
#    global enemies
    global map1
    global camx
    global gravity
    if mouseheld:
        if time.time()-players[-1].lastshot>=players[-1].cd:
            players[-1].shoot(0,turn, mousex-players[-1].graphicx, mousey-players[-1].y-players[-1].hitboxh//2)
    for e in map1:
        e.graphicx=e.x-camx
    for e in players:
        e.graphicx=e.x-camx
        if ScanDown(e.x,e.y,map1):
            e.v-=gravity
        else:
            e.v=max(e.v,0)
        e.y+=max(e.v,-ScanDown(e.x,e.y,map1))
        if e.y<0:
            e.die(0,turn)
#    for e in enemies:
#        e.graphicx=e.x-camx
#        if ScanDown(e.x,e.y,map1):
#            e.v-=gravity
#        else:
            e.v=max(e.v,0)
#        e.y+=max(e.v,-ScanDown(e.x,e.y,map1))
    place.push_handlers(keys)
    if keys[key.D]:
        players[-1].d(0,turn)
    if keys[key.A]:
        players[-1].a(0,turn)
    clock.schedule_once(tick,0.01)
tick(0)

def grq():
    time.sleep(1)
    return 200
"""
class myThread (threading.Thread):
   def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.e=threading.Event()
   def run(self):
      while True:
          self.e.wait()
          for e in players:
              e.y+=grq()
          self.e.clear()
   def fff(self):
       self.e.set()

thread1=myThread(1)
thread1.start()
"""

@place.event
def on_key_press(symbol, modifiers):
    global players
    global BasicGuy
    global turn
    global player_side
    if symbol==key.W:
        for e in players:
            if e.active==1:
                e.w(0,turn)
    if symbol==key.V:
        player_side=1-player_side
        new_clone()
    #if symbol==key.B:
    #    thread1.fff()

def choose_clone():
    global players
    global BasicGuy
    global turn
    global CCpics
    global clone_frame
    global player_side
    CCpics=[]
    for i in range(len(possible_units)):
        CCpics.append([clone_frame,i*290+20,20])
        if player_side==0: 
            CCpics.append([possible_units[i][7].get_region(0,0,249,350),50+i*290,50])
            CCpics[-1][0].width=200
            CCpics[-1][0].height=350
        else:
            CCpics.append([possible_units[i][12].get_region(0,0,249,350),50+i*290,50])
            CCpics[-1][0].width=200
            CCpics[-1][0].height=350

    

def new_clone():
    global players
    global BasicGuy
    global turn
    global camx
    camx=0
    clock.unschedule(tick)
    for e in bullets:
        clock.unschedule(e.fly)
    for e in players:
        clock.unschedule(e.shoot)
        clock.unschedule(e.w)
        clock.unschedule(e.d)
        clock.unschedule(e.a)
        clock.unschedule(e.die)
    choose_clone()



@place.event
def on_key_release(symbol, modifiers):
    pass

@place.event
def on_draw():
    place.clear()
    glEnable(GL_BLEND)
    for e in map1+bullets:
        e.draw()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for e in players:
        e.draw()
    for e in CCpics:
        e[0].blit(e[1],e[2])
    

pyglet.app.run()
