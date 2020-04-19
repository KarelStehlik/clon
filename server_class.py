from imports import *
class platform():
    x=0
    y=0
    height=0
    width=0

map1=[]
floor=platform()
floor.width=20000
floor.height=20
floor.x=-600
map1.append(floor)
platform1=platform()
platform1.height=30
platform1.width=200
platform1.x=500
platform1.y=100
map1.append(platform1)
platform2=platform()
platform2.height=30
platform2.width=200
platform2.x=200
platform2.y=200
map1.append(platform2)
maps=[map1]

class bullet():
    x=100
    y=100
    vx=0
    vy=0
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

class player():
    side=0
    maxhp=50
    dmg=5
    cd=0.6
    bulletspeed=4.2
    rang=600
    hitboxw=30
    hitboxh=70
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
    hp=50
    dead=0
    lastshot=time.time()
    shooting=False
    walkingA=False
    walkingD=False
    
    def attempt_to_shoot(self,x,y):
        t=time.time()
        if t-self.lastshot>=self.cd:
            self.shoot(x,y)
            self.lastshot=time.time()
        elif t-self.lastshot>=self.cd-0.3:
            clock.schedule_once(lambda dt: shoot(x,y),self.cd-t+self.lastshot )
    
    def ScanDown(self,map1):
        r=100000000
        for e in map1:
            if e.x<x and e.x+e.width>self.x and e.y+e.height<=self.y:
                r=min(r,self.y-e.y-e.height)
        return(r)
    
    def fall(self,map1):
        if self.ScanDown(map1):
            self.v-=gravity
        else:
            self.v=max(self.v,0)
        self.y+=max(self.v,-ScanDown(self.x,self.y,map1))
        if self.y<0:
            self.die(0,turn)
            self.v=max(self.v,0)
            
    def die(self,t):
        if t==turn:
            self.dead=1
            if self.active==1:
                self.log.append(["ded",time.time()-self.t1])
            self.active=0
            
    def takedmg(self,amount):
        if self.dead==0:
            self.hp-=amount
            if self.hp<=0:
                self.die(0,turn)
                
    def a(self):
        if self.dead==0:
            self.x-=min(self.walkspeed,self.x)
            if self.active==1:
                self.log.append(["a",time.time()-self.t1])           
                            
    def d(self):
        if self.dead==0:
            self.x+=self.walkspeed
            if self.active==1:
                self.log.append(["d",time.time()-self.t1])
                            
    def w(self):
        if self.dead==0:
            global map1
            if ScanDown(self.x,self.y,map1)==0:
                self.v=self.jumppower
                if self.active==1:
                    self.log.append(["w",time.time()-self.t1])

    def shoot(self,x,y):
        if self.dead==0:
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
            shot.fly(0)
            if self.active==1:
                self.log.append(["S",time.time()-self.t1,x,y])
    def run(self):
        global turn
        global camx
        if self.active==0:
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


        #hp dmg  aspd bspd range   hbxX hbxY
BasicGuy=[50,20,   0.7,5.2 ,550,   30,   70,
          3.5,14]
        #spd  jump

BasicGuy2=[100,5, 0.05,0.5 ,1.1,   35,   60,
          5,16]
possible_units=[]
possible_units.append(BasicGuy)
possible_units.append(BasicGuy2)

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

