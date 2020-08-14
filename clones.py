import images
import pyglet
import time
import numpy as np
import math
from constants import *
dudeg=pyglet.graphics.OrderedGroup(2)
def rect_intersect(ax1,ay1,ax2,ay2,bx1,by1,bx2,by2):
    return ax1<=bx2 and bx1<=ax2 and ay1<=by2 and by1<=ay2
def take_second(l):
    return l[1]
class clone():
    def __init__(self,mapp,l,batch,win,**kwargs):
        self.side=kwargs["side"]
        print(self.cost)
        if self.side==0:
            self.skin=self.imageG
        else:
            self.skin=self.imageR
        self.cost=kwargs["cost"]
        self.maxhp=kwargs["hp"]
        self.hp=self.maxhp
        self.height=kwargs["height"]
        self.width=kwargs["width"]
        self.batch=batch
        self.spd=kwargs["spd"]
        self.jump=kwargs["jump"]
        self.win=win
        self.mapp=mapp
        self.active=True
        self.exists=False
        self.vx=self.vy=0
        self.log=[]
        self.log_completed=0
        self.exist_time=0
        l[self.side]+=[self]
        self.l=l
        self.facing=-1
        self.hpbar_scale=self.width/images.buttonG.width
        if self.side==0:
            self.x=10
        else:
            self.x=1270
        self.y=100
        self.sprite=pyglet.sprite.Sprite(self.skin,10,100,batch=self.batch,group=dudeg)
        self.hpbar=pyglet.sprite.Sprite(images.buttonG,self.x,self.y+self.height,batch=self.batch,group=dudeg)
        self.hpbar.scale=self.hpbar_scale
        self.hpbar.scale_y=5/self.hpbar.height
        self.additional_images=[]
        arro=[images.blue_arrow,images.red_arrow][self.side]
        self.additional_images.append([pyglet.sprite.Sprite(arro,
                                                           x=self.x*SPRITE_SIZE_MULT,
                                                           y=(self.y+self.height+10)*SPRITE_SIZE_MULT,
                                                            group=dudeg,batch=self.batch),
                                       0,self.height+10])
    def start(self):
        if self.side==0:
            self.x=10
        else:
            self.x=1270
        self.y=100
        self.sprite.batch=self.batch
        self.hpbar.batch=self.batch
        self.hpbar.scale_x=1
        self.hp=self.maxhp
        self.exists=True
        self.log_completed=0
        self.exist_time=0
    def update_pos(self,x,y):
        self.x=x
        self.y=y
        for e in self.additional_images:
            e[0].update(x=(self.x+e[1])*SPRITE_SIZE_MULT,y=(self.y+e[2])*SPRITE_SIZE_MULT)
        self.sprite.update(x=self.x*SPRITE_SIZE_MULT,y=self.y*SPRITE_SIZE_MULT)
        self.hpbar.update(x=(self.x-self.width//2)*SPRITE_SIZE_MULT,y=(self.y+self.height)*SPRITE_SIZE_MULT)
    def take_damage(self,amount,source):
        self.hp-=amount
        if self.hp<=0:
            self.win.money+=self.cost//2+25
            self.die()
            return
        self.hpbar.scale_x=self.hp/self.maxhp
    def on_ground(self):
        for e in self.mapp.platforms:
            if self.y==e.y+e.h and e.x<self.x<e.x+e.w:
                return True
        return False
    def a_start(self):
        if self.active:
            self.log.append(["a",self.exist_time])
        self.vx=-self.spd
        self.sprite.scale_x=-1
        self.facing=-1
    def move_stop(self):
        if self.active:
            self.log.append(["stop",self.exist_time])
        self.vx=0
    def d_start(self):
        if self.active:
            self.log.append(["d",self.exist_time])
        self.vx=self.spd
        self.sprite.scale_x=1
        self.facing=1
    def w(self):
        if self.active:
            self.log.append(["w",self.exist_time])
        if self.on_ground():
            self.vy=self.jump
    def move(self,dt):
        if self.exists:
            self.exist_time+=dt
            if not self.active:
                for e in self.log[self.log_completed::]:
                    if e[1]<self.exist_time:
                        self.log_completed+=1
                        if e[0]=="d":
                            self.d_start()
                        elif e[0]=="stop":
                            self.move_stop()
                        elif e[0]=="a":
                            self.a_start()
                        elif e[0]=="w":
                            self.w()
                        elif e[0]=="shoot":
                            self.shoot(e[2],dt)
                        elif e[0]=="die":
                            self.die()
                            return
                    else:
                        break
            self.x+=self.vx*dt
            ycap=0
            for e in self.mapp.platforms:
                if self.y>e.y and self.vy<0 and rect_intersect(self.x,
                                                               self.y+self.vy*dt,
                                                               self.x,
                                                               self.y,
                                                               e.x,e.y+e.h,e.x+e.w,e.y+e.h):
                    ycap=max(e.y+e.h,ycap)
            self.y=max(ycap,self.y+self.vy*dt)
            if not ycap==0:
                self.vy=0
            self.update_pos(self.x,self.y)
    def die(self):
        if self.exists:
            if self.active:
                self.log.append(["die",self.exist_time])
                self.active=False
                self.additional_images=[]
                self.log.sort(key=take_second)
            self.vx=0
            self.vy=0
            self.sprite.batch=None
            self.hpbar.batch=None
            self.exists=False
class Projectile():
    def __init__(self,x,y,vx,vy,enemies,rang,damage,l,batch,model):
        self.x,self.y,self.vx,self.vy=x,y,vx,vy
        self.enemies=enemies
        self.sprite=pyglet.sprite.Sprite(model,x,y,batch=batch,group=dudeg)
        self.l=l
        self.l.append(self)
        self.rang=rang
        self.speed=math.sqrt(self.vx**2+self.vy**2)
        pyglet.clock.schedule_once(self.die,self.rang/self.speed)
        self.damage=damage
    def move(self,dt):
        self.x+=self.vx*dt
        self.y+=self.vy*dt
        if self.collide():
            return
        self.sprite.update(x=SPRITE_SIZE_MULT*self.x,y=SPRITE_SIZE_MULT*self.y)
    def collide(self):
        for e in self.enemies:
            if e.exists and e.x-e.width/2<self.x<e.x+e.width/2 and e.y<self.y<e.y+e.height:
                self.on_collision(e)
                return True
        return False
    def on_collision(self,e):
        pass
    def die(self,dt):
        self.l.remove(self)
        self.sprite.delete()
        del self
###################################################################################################
class BasicGuyBullet(Projectile):
    def __init__(self,x,y,vx,vy,enemies,rang,damage,l,batch):
        super().__init__(x,y,vx,vy,enemies,rang,damage,l,batch,images.bullet)
    def on_collision(self,e):
        e.take_damage(self.damage,self)
        pyglet.clock.unschedule(self.die)
        self.die(0)
class BasicGuy(clone):
    cost=0
    imageG=images.gunmanG
    imageR=images.gunmanR
    def __init__(self,mapp,l,bulletlist,batch,side,win):
        super().__init__(mapp,l,batch,win,hp=50,height=70,
                         width=30,spd=200,jump=600,side=side,
                         cost=self.cost)
        self.dmg=20
        self.aspd=0.7
        self.bspd=400
        self.rang=400
        self.bulletlist=bulletlist
        self.lastshot=0
    def shoot(self,a,dt):
        x=a[0]
        y=a[1]
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/math.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        if self.active:
            self.log.append(["shoot",self.exist_time,[x,y]])
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.bulletlist,self.batch)
        a.move(0.05)
    def attempt_shoot(self,a,time,dt):
        t=time
        if t-self.lastshot>self.aspd:
            self.shoot(a,dt)
            self.lastshot=t
###########################################################################################################
class Mixer(clone):
    cost=50
    imageG=images.mixerG
    imageR=images.mixerR
    def __init__(self,mapp,l,bulletlist,batch,side,win):
        super().__init__(mapp,l,batch,win,hp=100,height=60,
                         width=30,spd=300,jump=700,side=side,
                         cost=self.cost)
        self.dmg=200
        self.lastshot=0
        self.enemies=l[1-self.side]
    def shoot(self,a,dt):
        for e in self.enemies:
            if e.exists and e.x-e.width/2<self.x<e.x+e.width/2 and e.y<self.y+self.height/2<e.y+e.height:
                e.take_damage(self.dmg*dt,self)
    def attempt_shoot(self,a,time,dt):
        pass
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot([],dt)
#########################################################################################################
class Bazooka(clone):
    imageG=images.ZookaG
    imageR=images.ZookaR
    cost=500
    def __init__(self,mapp,l,bulletlist,batch,side,win):
        super().__init__(mapp,l,batch,win,hp=150,height=65,
                         width=65,spd=200,jump=600,side=side,
                         cost=self.cost)
        self.dmg=70
        self.aspd=3
        self.bspd=500
        self.rang=800
        self.bulletlist=bulletlist
        self.lastshot=0
        self.eradius=150
    def shoot(self,a,dt):
        x=a[0]
        y=a[1]
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/math.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        if self.active:
            self.log.append(["shoot",self.exist_time,a])
        a=BazookaBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.bulletlist,self.batch,self.eradius)
        a.move(0.05)
    def attempt_shoot(self,a,time,dt):
        t=time
        if t-self.lastshot>self.aspd:
            self.shoot(a,0)
            self.lastshot=t
class BazookaBullet(Projectile):
    def __init__(self,x,y,vx,vy,enemies,rang,damage,l,batch,radius):
        super().__init__(x,y,vx,vy,enemies,rang,damage,l,batch,images.BazookaBullet)
        self.radius=radius
        if vx==0:
            if vy<0:
                self.sprite.rotation=-90
            else:
                self.sprite.rotation==90
        elif vx>0:
            self.sprite.rotation=-math.atan(vy/vx)*180/math.pi
        else:
            self.sprite.rotation=180-math.atan(vy/vx)*180/math.pi
    def on_collision(self,e):
        for i in self.enemies:
            if i.exists and (i.x-self.x)**2+(i.y+i.height//2-self.y)**2<=self.radius**2:
                i.take_damage(self.damage,self)
        pyglet.clock.unschedule(self.die)
        self.die(0)
##################################################################################################################
class Tele(clone):
    cost=250
    imageG=images.teleG
    imageR=images.teleR
    def __init__(self,mapp,l,bulletlist,batch,side,win):
        super().__init__(mapp,l,batch,win,hp=50,height=80,
                         width=44,spd=200,jump=600,side=side,
                         cost=self.cost)
        self.dmg=60
        self.aspd=3
        self.lastshot=0
        self.radius=200
        self.enemies=l[1-side]
        self.phase=255
    def shoot(self,a,dt):
        if self.active:
            self.log.append(["shoot",self.exist_time,a])
        self.update_pos(self.x+a[0]/SPRITE_SIZE_MULT,self.y+a[1]/SPRITE_SIZE_MULT)
        self.phase=0
    def attempt_shoot(self,a,time,dt):
        t=time
        if t-self.lastshot>self.aspd and self.exist_time>3:
            self.shoot(a,0)
            self.lastshot=t
    def move(self,dt):
        if (not self.phase==255) and self.exists:
            self.exist_time+=dt
            self.phase=min(self.phase+150*dt,255)
            self.sprite.opacity=self.phase
            if self.phase==255:
                for i in self.enemies:
                    if i.exists and (i.x-self.x)**2+(i.y+i.height//2-self.y)**2<=self.radius**2:
                        i.take_damage(self.dmg,self)
        else:
            super().move(dt)
    def die(self):
        self.phase=255
        self.sprite.opacity=self.phase
        super().die()
############################################################################
class Shield(clone):
    cost=0
    imageG=images.teleG
    imageR=images.teleR
    def __init__(self,mapp,l,bulletlist,batch,side,win):
        super().__init__(mapp,l,batch,win,hp=500,height=110,
                             width=70,spd=200,jump=600,side=side,
                             cost=self.cost)
        self.dmg=20
        self.aspd=0.7
        self.bspd=400
        self.rang=400
        self.bulletlist=bulletlist
        self.lastshot=0
    def shoot(self,a,dt):
        x=a[0]
        y=a[1]
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/math.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        if self.active:
            self.log.append(["shoot",self.exist_time,[x,y]])
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.bulletlist,self.batch)
        a.move(0.05)
    def attempt_shoot(self,a,time,dt):
        t=time
        if t-self.lastshot>self.aspd:
            self.shoot(a,dt)
            self.lastshot=t
    def take_damage(self,amount,source):
        if (source.x>self.x and self.facing==1) or (source.x<self.x and self.facing==-1):
            super().take_damage(amount/20,source)
        else:
            super().take_damage(amount,source)


possible_units=[BasicGuy,Mixer,Bazooka,Tele,Shield]
