from imports import *
import threading
place = pyglet.window.Window(resizable=True,caption='CLOWN WARS!')
keys = key.KeyStateHandler()
place.set_minimum_size(100,100)
pyglet.gl.glClearColor(0.2,0.3,1,1)
players=[]
map1=[]
camx=0
bullets=[]
gravity=0.65
turn=0
#player_side=int(requests.get("http://localhost:5000/GetSide").text)
player_side=0
CCpics=[]
clone_frame=pyglet.resource.image('clone_select.png')
clone_frame.width=270
clone_frame.height=430
clone_frame=pyglet.sprite.Sprite(clone_frame)

class platform:
    graphicx=0
    def __init__(self,w,h,x,y):
        global map1
        self.pic=pyglet.resource.image('platform.png')
        self.width=w
        self.height=h
        self.x=x
        self.y=y
        self.pic=pyglet.sprite.Sprite(self.pic,x,y)
        self.pic.scale_x=w/self.pic.width
        self.pic.scale_y=h/self.pic.height
        map1.append(self)
    def draw(self):
        self.pic.x=self.graphicx
        self.pic.draw()
        
floor=platform(20000,20,-600,0)

platform1=platform(200,30,500,100)

platform2=platform(200,30,200,200)

mouseheld=False
mousex=0
mousey=0

class bullet():
    x=100
    y=100
    vx=0
    vy=0
    graphicx=0
    model=pyglet.resource.image('Bullet.png')
    side=1
    dmg=5
    lifespan=100
    dead=0
    def die(self):
        self.dmg=0
        global bullets
        bnew=[]
        for e in bullets:
            if e!=self:
                bnew.append(e)
        bullets=bnew
        self.dead=1
        del self
    def fly(self):
        self.x+=self.vx
        self.y+=self.vy
        self.lifespan-=1
        if self.lifespan<=0:
            self.die()
        if self.dead==0:
            for e in players:
                if (e.x-e.hitboxw//2<self.x<e.x+e.hitboxw//2) and (e.y<self.y<e.y+e.hitboxh) and (self.side != e.side):
                    if e.dead==0:
                        e.takedmg(0,self.dmg)
                        self.die()
    def draw(self):
        global camx
        self.graphicx=self.x-camx
        self.model.blit(self.graphicx,self.y)


        

def ScanDown(x,y,map1):
    r=100000000
    for e in map1:
        if e.x<x and e.x+e.width>x and e.y+e.height<=y:
            r=min(r,y-e.y-e.height)
    return(r)


class player():
    side=0
    maxhp=50
    dmg=5
    cd=0.6
    bulletspeed=4.2
    rang=600
    hitboxw=30
    hitboxh=70
    skin=0
    sk=0
    facing=1
    x=50
    y=300
    v=0
    walkspeed=3
    active=1
    log=[]
    a=0
    d=0
    t1=time.time()
    jumppower=11
    graphicx=0
    hp=50
    dead=0
    a=pyglet.resource.image('GreenButton.png')
    a.width=hitboxw
    a.height=hitboxw//5
    hpgreen=pyglet.sprite.Sprite(a)
    hpred=pyglet.resource.image('RedButton.png')
    hpgreen_width=hitboxw
   # hpred.width=hitboxw
  #  hpgreen.height=int(hitboxw//5)
    hpred.height=hitboxw//5
    lastshot=time.time()
    def die(self,dt,t):
        if t==turn:
            self.dead=1
            if self.active==1:
                self.log.append(["ded",time.time()-self.t1])
            self.active=0
    def takedmg(self,dt,amount):
        if self.dead==0:
            self.hp-=amount
            if self.hp<=0:
                self.die(0,turn)
            else:
                self.hpgreen_width=self.hitboxw*self.hp//self.maxhp
    def draw(self):
        if self.dead==0:
            self.hpred.width=self.hpred_width
            self.hpred.blit(self.graphicx-self.hitboxw//2,self.y+self.hitboxh)
            self.hpgreen.scale_x=self.hp/self.maxhp
            self.hpgreen.x=self.graphicx-self.hitboxw//2
            self.hpgreen.y=self.y+self.hitboxh
            self.hpgreen.draw()
            if self.facing==1:
                self.skin.blit(self.graphicx-self.hitboxw//2,self.y)
            else:
                self.sk.blit(self.graphicx-self.hitboxw//2+240,self.y)

                
    def a(self,dt,t):
        if self.dead==0 and t==turn:
            global camx
            self.x-=min(self.walkspeed,self.x)
            self.facing=-1
            if self.active==1:
                self.log.append(["a",time.time()-self.t1])
                if self.x-camx<place.width//2:
                    camx=max(self.x-(place.width//2),0)
            
                            
    def d(self,dt,t):
        if self.dead==0 and t==turn:
            global camx
            self.x+=self.walkspeed
            self.facing=1
            if self.active==1:
                self.log.append(["d",time.time()-self.t1])
                if self.x-camx>place.width//2:
                    camx=self.x-(place.width//2)
            
                
    def w(self,dt,t):
        if self.dead==0 and t==turn:
            global map1
            if ScanDown(self.x,self.y,map1)==0:
                self.v=self.jumppower
                if self.active==1:
                    self.log.append(["w",time.time()-self.t1])

    def shoot(self,dt,t,x,y):
        if self.dead==0 and t==turn:
            if x==0:
                x=1
            if y==0:
                y=1
            global bullets
            shot=bullet()
            shot.side=self.side
            shot.vx=self.bulletspeed/math.sqrt(y*y/(x*x)+1)
            if x<0:
                shot.vx*=-1
            shot.vy=shot.vx*y/x
            shot.dmg=self.dmg
            shot.x=self.x
            shot.y=self.y+self.hitboxh//2
            shot.lifespan=self.rang//self.bulletspeed
            bullets.append(shot)
            self.lastshot=time.time()
            if self.active==1:
                self.log.append(["S",time.time()-self.t1,x,y])
            
        #hp dmg  aspd bspd range   hbxX hbxY
BasicGuy=[50,20,   0.7,5.2 ,550,   30,   70,
          pyglet.resource.image('GGunman.png'),
          pyglet.resource.image('GGunman.png').get_transform(flip_x=True, flip_y=False, rotate=0),
          3.5,14,pyglet.resource.image('BGunman.png'),
          pyglet.resource.image('BGunman.png').get_transform(flip_x=True, flip_y=False, rotate=0)]
        #spd  jump

BasicGuy2=[100,5, 0.05,0.5 ,1.1,   35,   60,
          pyglet.resource.image('GMixer.png'),
          pyglet.resource.image('GMixer.png').get_transform(flip_x=True, flip_y=False, rotate=0),
          5,16,pyglet.resource.image('BMixer.png'),
          pyglet.resource.image('BMixer.png').get_transform(flip_x=True, flip_y=False, rotate=0)]

possible_units=[]
possible_units.append(BasicGuy)
possible_units.append(BasicGuy2)

BasicGuy[8].width=40
BasicGuy[8].height=70
BasicGuy[7].width=40
BasicGuy[7].height=70
BasicGuy[11].width=40
BasicGuy[11].height=70
BasicGuy[12].width=40
BasicGuy[12].height=70

BasicGuy2[8].width=35
BasicGuy2[8].height=60
BasicGuy2[7].width=35
BasicGuy2[7].height=60
BasicGuy2[11].width=35
BasicGuy2[11].height=60
BasicGuy2[12].width=35
BasicGuy2[12].height=60

BasicGuy2[8].anchor_x-=11
BasicGuy2[12].anchor_x-=11

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
    p1.hpgreen.scale_x=1
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
    for e in bullets:
        e.fly()
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
    
clock.schedule_interval(tick,0.01)

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

