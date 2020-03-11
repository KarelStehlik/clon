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
class platform():
    x=0
    y=0
    height=0
    width=0
    pic=0
    graphicx=0
    pic=pyglet.resource.image('platform.png')
    def draw(self):
        self.pic.width=self.width
        self.pic.height=self.height
        self.pic.blit(self.graphicx,self.y)
floor=platform()
floor.width=20000
floor.height=20
floor.x=-600
floor.graphicx=-600
map1.append(floor)
platform1=platform()
platform1.height=30
platform1.width=200
platform1.x=500
platform1.graphicx=500
platform1.y=100
map1.append(platform1)
platform2=platform()
platform2.height=30
platform2.width=200
platform2.x=200
platform2.graphicx=200
platform2.y=200
map1.append(platform2)
player_side=requests.get('http://127.0.0.1:5000/GetSide')

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
    hpgreen=copy.copy(pyglet.resource.image('GreenButton.png'))
    hpred=pyglet.resource.image('RedButton.png')
    hpgreen_width=hitboxw
    hpred.width=hitboxw
    hpgreen.height=hitboxw//5
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
            self.hpgreen.width=self.hpgreen_width
            self.hpgreen.blit(self.graphicx-self.hitboxw//2,self.y+self.hitboxh)
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
            shot.fly(0)
            self.lastshot=time.time()
            if self.active==1:
                self.log.append(["S",time.time()-self.t1,x,y])
