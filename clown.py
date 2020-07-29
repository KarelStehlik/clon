from imports import *
import threading
keys = key.KeyStateHandler()
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

def tick(dt):
    global players
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
            e.v=max(e.v,0)
    place.push_handlers(keys)
    if keys[key.D]:
        players[-1].d(0,turn)
    if keys[key.A]:
        players[-1].a(0,turn)

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

##########################################################
class minimode_choosing():
    def __init__(self,**kwargs):
        self.pics_clonesG=[]
        self.pics_clonesR=[]
        self.pics_frames=[pyglet.sprite.Sprite(images.cloneFrame,i*290+20,
                          20) for i in range(len(self.possible_clones))]
        self.pics_clones=[]
        self.batch_red=pyglet.graphics.Batch()
        self.batch_green=pyglet.graphics.Batch()
        self.shift=0
        self.win=kwargs["win"]
    def mouse_move(self,x,y,dx,dy):
        if x<40:
            self.shift-=2
            for e in self.pics_frames+self.pics_clones:
                e.x+=2
        if x>self.win.width-40:
            self.shift+=2
            for e in self.pics_frames+self.pics_clones:
                e.x-=2
    def mouse_press(self,x,y,button,modifiers):
        i=0
        for e in self.pics_frames:
            if e.x<x<e.x+e.width and a.y<y<e.height:
                choice=possible_units[i]
                players[-1].die(0,turn)
                turn+=1
                Spawn(clone_choice,player_side)
                for k in bullets:
                    k.die()
                return
            i+=1
class mode_testing():
    def __init__(self,**kwargs):
        global testBlocks
        self.mainBatch = pyglet.graphics.Batch()
        self.fpscount=pyglet.text.Label(x=5,y=5,text="aaa",color=(255,255,255,255))
        self.win=kwargs["win"]
        self.mousex,self.mousey,self.frames,self.sec,self.camx,self.mouseheld=0,0,0,0,0,False
        self.choosing_clones,self.cc=False,minimode_choosing(win=self.win)
        self.players=[]
        self.turn,self.turnTime=0,0
    def new_clone():
        self.camx=0
        self.turn+=1
        self.turnTime=0
        choose_clone()
    def mouse_move(self,x, y, dx, dy):
        self.mousex=x
        self.mousey=y
        if self.choosing_clones:
            self.cc.mouse_move(x,y,dx,dy)
    def mouse_drag(self,x, y, dx, dy, button, modifiers):
        self.mouse_move(x,y,dx,dy)
    def tick(self,dt):
        self.win.switch_to()
        self.draw_all()
        self.fpscount.draw()
        self.check(dt)
        self.win.flip()
    def check(self,dt):
        self.sec+=dt
        self.frames+=1
        if self.sec>1:
            self.sec-=1
            self.fpscount.text=str(self.frames)
            self.frames=0
    def draw_all(self):
        self.win.clear()
        self.mainBatch.draw()
    def key_press(self,symbol,modifiers):
        if symbol==key.W:
            self.activePlayer.w(0,turn)
        if symbol==key.V:
            player_side=1-player_side
            new_clone()
    def mouse_press(self,x,y,button,modifiers):
        self.mouseheld=True
        if self.choosing_clones:
            self.cc.mouse_press(x,y,button,modifiers)
    def mouse_release(self,x,y,button,modifiers):
        self.mouseheld=False

class windoo(pyglet.window.Window):
    def start(self):
        self.currentMode=mode_testing(win=self)
    def on_mouse_motion(self,x, y, dx, dy):
        self.currentMode.mouse_move(x,y,dx,dy)
    def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
        self.currentMode.mouse_drag(x,y,dx,dy,button,modifiers)
    def on_close(self):
        self.close()
        os._exit(0)
    def tick(self,dt):
        self.dispatch_events()
        self.currentMode.tick(dt)
    def on_key_press(self,symbol,modifiers):
        self.currentMode.key_press(symbol,modifiers)
    def on_mouse_release(self, x, y, button, modifiers):
        self.currentMode.mouse_release(x,y,button,modifiers)
place = windoo(resizable=True,caption='test')
display = pyglet.canvas.Display()
screen = display.get_default_screen()
place.set_size(int(screen.width*0.45),int(screen.height*2/3))
place.set_location(screen.width//2,int(screen.height*1/6))
place.start()
pyglet.clock.schedule_interval(place.tick,1.0/60)
while True:
    pyglet.clock.tick()
