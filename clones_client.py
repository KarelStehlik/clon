import images
import pyglet
import time
import numpy as np
import math
import random
from constants import *
dudeg=pyglet.graphics.OrderedGroup(2)
projectileg=pyglet.graphics.OrderedGroup(3)
camx=0
clone_stats={}
def load_stats():
    global clone_stats
    with open("clone_stats.txt","r") as cs:
        clones=cs.read().split("\n")
        for clone in clones:
            name_stats=clone.split(":")
            stats={}
            for e in name_stats[1].split(","):
                k=e.split("=")
                stats[k[0]]=float(k[1])
            clone_stats[name_stats[0]]=stats
load_stats()

def get_cost(c):
    return c.cost

class Game():
    def __init__(self,mapp,batch,connection,gravity,side=0):
        self.clones=[[],[]]
        self.current_clones=[None,None]
        self.side=side
        self.mapp=mapp
        self.batch=batch
        self.connection=connection
        self.gravity=gravity
        self.bullets=[]
        self.particles=[]
        self.deadclones=[]
    def start_round(self):
        for e in self.clones[0]:
            e.start()
        for e in self.clones[1]:
            e.start()
    def summon(self,n,side):
        self.current_clones[side]=possible_units[n](self,
                                                    side)
    def tick(self,dt,mouseheld,mousex,mousey):
        if mouseheld:
                a=self.current_clones[self.side]
                if a.can_shoot():
                    self.connection.Send({"action": "shoot",
                                     "a": [mousex/SPRITE_SIZE_MULT-1280/2,
                                     mousey/SPRITE_SIZE_MULT-a.y-a.height/2]})
        for i in range(len(self.deadclones)):
            deed=self.deadclones.pop(0)
            deed.die()
        for e in self.clones[0]:
            e.move(dt)
        for e in self.clones[1]:
            e.move(dt)
        for e in self.bullets:
            e.move(dt)
        for e in self.particles:
            e.tick(dt)
    def get_vpoint(self):
        return self.current_clones[self.side].vpoint
class particle():
    def __init__(self,x,y,size,duration,game):
        self.x,self.y=x,y
        self.sprite=pyglet.sprite.Sprite(self.img,x,y,
                                         batch=game.batch,
                                         group=projectileg)
        self.sprite.scale=size*SPRITE_SIZE_MULT/self.sprite.width
        self.existtime=0
        self.duration=duration
        game.particles.append(self)
        self.game=game
    def tick(self,dt):
        self.existtime+=dt
        self.sprite.x,self.sprite.y=(self.x-camx)*SPRITE_SIZE_MULT,self.y*SPRITE_SIZE_MULT
        if self.existtime>self.duration:
            self.die()
    def die(self):
        self.game.particles.remove(self)
        self.sprite.delete()
        del self
class fire(particle):
    img=images.fire
    def __init__(self,x,y,size,duration,game,vy=0,vx=0,growth=0.003):
        super().__init__(x,y,size,duration,game)
        self.sprite.rotation=random.randint(0,359)
        self.vy=vy
        self.vx=vx
        self.growth=growth
    def tick(self,dt):
        if self.existtime>self.duration:
            super().die()
            return
        self.y+=self.vy*dt
        self.x+=self.vx*dt
        self.sprite.opacity=255*(1-self.existtime/self.duration)
        self.sprite.scale+=self.growth*dt*SPRITE_SIZE_MULT
        super().tick(dt)
class earth(particle):
    img=images.earthquack
    def __init__(self,x,y,size,duration,game,vy=0,growth=0.003):
        super().__init__(x,y,size,duration,game)
        self.vy=vy
        self.growth=growth
        self.sprite.scale_y=0
    def tick(self,dt):
        if self.existtime>self.duration:
            super().die()
            return
        self.y+=self.vy*dt
        self.sprite.opacity=255*(1-(self.existtime/self.duration)**2)
        self.sprite.scale_y+=self.growth*dt*SPRITE_SIZE_MULT
        super().tick(dt)
def rect_intersect(ax1,ay1,ax2,ay2,bx1,by1,bx2,by2):
    return ax1<=bx2 and bx1<=ax2 and ay1<=by2 and by1<=ay2
def take_second(l):
    return l[1]
class clone():
    def __init__(self,game,**kwargs):
        self.side=kwargs["side"]
        self.game=game
        stats=clone_stats[self.name]
        self.stats=stats
        if self.side==0:
            self.skin=self.imageG
        else:
            self.skin=self.imageR
        self.maxhp=stats["hp"]
        self.hp=self.maxhp
        self.height=stats["height"]
        self.width=stats["width"]
        self.spd=stats["spd"]
        self.jump=stats["jump"]
        self.active=True
        self.exists=False
        self.vx=self.vy=0
        self.log=[]
        self.log_completed=0
        self.exist_time=0
        game.clones[self.side].append(self)
        self.enemies=game.clones[1-self.side]
        self.facing=1
        self.moving=0
        self.move_locked=False
        self.hpbar_scale=SPRITE_SIZE_MULT*self.width/images.buttonG.width
        if self.side==0:
            self.x=10
        else:
            self.x=1270
        self.y=100
        self.vpoint=self.x-1280/2
        self.sprite=pyglet.sprite.Sprite(self.skin,10,100,batch=self.game.batch,group=dudeg)
        self.hpbar=pyglet.sprite.Sprite(images.buttonG,self.x,self.y+self.height,batch=self.game.batch,group=dudeg)
        self.hpbar.scale=self.hpbar_scale
        self.hpbar.scale_y=5/self.hpbar.height
        arro=[images.blue_arrow,images.red_arrow][self.side]
        self.additional_images=[]
        self.additional_images.append([pyglet.sprite.Sprite(arro,
                                        x=self.x*SPRITE_SIZE_MULT,
                                        y=(self.y+self.height+10)*SPRITE_SIZE_MULT,
                                        group=projectileg,batch=self.game.batch),
                                       0,self.height+10])
    def start(self):
        if self.side==0:
            self.x=10
        else:
            self.x=1270
        self.y=100
        self.sprite.batch=self.game.batch
        self.hpbar.batch=self.game.batch
        self.hpbar.scale_x=1
        self.hp=self.maxhp
        self.exists=True
        self.log_completed=0
        self.exist_time=0
        self.vx=self.vy=0
    def schedule_die(self):
        if self.exists:
            self.exists=False
            self.game.deadclones.append(self)
    def update_health(self,health):
        self.hp=health
        if self.hp<=0:
            self.schedule_die()
            return
        self.hpbar.scale_x=self.hp/self.maxhp
    def take_damage(self,amount,source):
        if self.exists and not self.active:
            self.update_health(self.hp-amount)
    def update_pos(self,x,y):
        self.sprite.update(x=(x-camx)*SPRITE_SIZE_MULT,y=y*SPRITE_SIZE_MULT)
        self.hpbar.update(x=(x-self.width//2-camx)*SPRITE_SIZE_MULT,y=(y+self.height)*SPRITE_SIZE_MULT)
        self.x,self.y=x,y
        self.vpoint=self.x-1280/2
        for e in self.additional_images:
            e[0].update(x=(self.x+e[1]-camx)*SPRITE_SIZE_MULT,y=(self.y+e[2])*SPRITE_SIZE_MULT)
    def on_ground(self):
        for e in self.game.mapp.platforms:
            if self.y==e.y+e.h and e.x<self.x<e.x+e.w:
                return True
        return False
    def a_start(self):
        if self.exists:
            self.sprite.scale_x=-1
            self.facing=-1
            self.moving=-1
            if not self.move_locked:
                self.vx=-self.spd
    def move_stop(self):
        if self.exists:
            self.moving=0
            if not self.move_locked:
                self.vx=0
    def d_start(self):
        if self.exists:
            self.sprite.scale_x=1
            self.facing=1
            self.moving=1
            if not self.move_locked:
                self.vx=self.spd
    def w(self):
        if self.on_ground() and self.exists:
            self.vy=self.jump
    def knockback(self,x,y):
        if self.exists:
            self.y+=1
            self.vx+=x
            self.vy+=y
            self.move_locked=True
    def distance_from_ground(self):
        d=10000
        for e in self.game.mapp.platforms:
            if e.x<self.x<e.x+e.w and e.y+e.h<=self.y:
                d=min(self.y-e.y-e.h,d)
        return d
    def move(self,dt):
        if self.exists:
            if self.move_locked and self.on_ground():
                self.move_locked=False
                self.vx=self.moving*self.spd
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
                            self.schedule_die()
                            return
                    else:
                        break
                self.x=self.x+self.vx*dt
                ycap=-500
                for e in self.game.mapp.platforms:
                    if self.y>e.y and self.vy<0 and rect_intersect(self.x,
                                                                   self.y+self.vy*dt,
                                                                   self.x,
                                                                   self.y,
                                                                   e.x,e.y+e.h,e.x+e.w,e.y+e.h):
                        ycap=max(e.y+e.h,ycap)
                self.y=max(ycap,self.y+self.vy*dt)
                if not ycap==-500:
                    self.stomp(-self.vy)
                    self.vy=0
                else:
                    self.vy-=self.game.gravity*dt
                if self.y<=-500:
                    self.schedule_die()
            self.update_pos(self.x,self.y)
    def stomp(self,amount):
        pass
    def die(self):
        if self.active:
            self.active=False
            self.log.sort(key=take_second)
            self.additional_images=[]
        self.vx=0
        self.vy=0
        self.moving=0
        self.sprite.batch=None
        self.hpbar.batch=None
        self.exists=False
class Projectile():
    def __init__(self,x,y,vx,vy,game,side,rang,damage,model):
        self.x,self.y,self.vx,self.vy=x,y,vx,vy
        self.enemies=game.clones[1-side]
        self.sprite=pyglet.sprite.Sprite(model,x,y,batch=game.batch,group=dudeg)
        self.l=game.bullets
        self.l.append(self)
        self.rang=rang
        self.speed=math.sqrt(self.vx**2+self.vy**2)
        pyglet.clock.schedule_once(self.die,self.rang/self.speed)
        self.damage=damage
        self.game=game
    def move(self,dt):
        self.x+=self.vx*dt
        self.y+=self.vy*dt
        self.sprite.update(x=SPRITE_SIZE_MULT*(self.x-camx),y=SPRITE_SIZE_MULT*self.y)
        self.collide()
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
def AOE_square(source,x,y,radius,targets,damage,knockback_x=0,knockback_y=0):
    for e in targets:
        if rect_intersect(x-radius,y-radius,x+radius,y+radius,e.x-e.width/2,
                          e.y,e.x+e.width/2,e.y+e.height):
            if (not knockback_x==0) or (not knockback_y==0):
                e.knockback(knockback_x,knockback_y)
            e.take_damage(damage,source)
def AOE_rect(source,x,y,x2,y2,targets,damage,knockback_x=0,knockback_y=0):
    for e in targets:
        if rect_intersect(x,y,x2,y2,e.x-e.width/2,
                          e.y,e.x+e.width/2,e.y+e.height):
            if (not knockback_x==0) or (not knockback_y==0):
                e.knockback(knockback_x,knockback_y)
            e.take_damage(damage,source)
###################################################################################################
class BasicGuyBullet(Projectile):
    def __init__(self,x,y,vx,vy,game,side,rang,damage):
        super().__init__(x,y,vx,vy,game,side,rang,damage,images.bullet)
    def on_collision(self,e):
        e.take_damage(self.damage,self)
        pyglet.clock.unschedule(self.die)
        self.die(0)
class BasicGuy(clone):
    name="BasicGuy"
    cost=clone_stats[name]["cost"]
    imageG=images.gunmanG
    imageR=images.gunmanR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.rang=self.stats["rang"]
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
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.game,self.side,
                         self.rang,self.dmg)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
###########################################################################################################
class Mixer(clone):
    name="Mixer"
    cost=clone_stats[name]["cost"]
    imageG=images.mixerG
    imageR=images.mixerR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.lastshot=0
        self.enemies=game.clones[1-self.side]
    def shoot(self,a,dt):
        AOE_square(self,self.x,self.y+self.height*2/3,self.width/2,self.enemies,self.dmg*dt)
    def can_shoot(self):
        return False
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot([],dt)
#########################################################################################################
class Bazooka(clone):
    name="Bazooka"
    cost=clone_stats[name]["cost"]
    imageG=images.ZookaG
    imageR=images.ZookaR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.rang=self.stats["rang"]
        self.lastshot=0
        self.eradius=self.stats["eradius"]
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
        a=BazookaBullet(self.x,self.y+self.height/2,vx,vy,self.game,self.side,
                         self.rang,self.dmg,self.eradius)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
class BazookaBullet(Projectile):
    def __init__(self,x,y,vx,vy,game,side,rang,damage,radius):
        super().__init__(x,y,vx,vy,game,side,rang,damage,images.BazookaBullet)
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
        AOE_square(self,self.x,self.y,self.radius,self.enemies,self.damage)
        fire(self.x,self.y,0,0.5,self.game,growth=self.radius/150)
        pyglet.clock.unschedule(self.die)
        self.die(0)
##################################################################################################################
class Tele(clone):
    name="Tele"
    cost=clone_stats[name]["cost"]
    imageG=images.teleG
    imageR=images.teleR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.lastshot=0
        self.radius=self.stats["radius"]
        self.enemies=game.clones[1-side]
        self.phase=255
    def shoot(self,a,dt):
        self.x+=a[0]
        self.y+=a[1]
        self.phase=0
        self.update_pos(self.x,self.y)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
    def move(self,dt):
        if self.phase != 255:
            self.exist_time+=dt
            self.update_pos(self.x,self.y)
            self.phase=min(self.phase+300*dt,255)
            self.sprite.opacity=self.phase
            if self.phase==255:
                AOE_square(self,self.x,self.y,self.radius,self.enemies,self.dmg)
        else:
            super().move(dt)
    def die(self):
        self.phase=255
        self.sprite.opacity=self.phase
        super().die()
##########################################################################
class Shield(clone):
    name="Shield"
    cost=clone_stats[name]["cost"]
    imageG=images.ShieldG
    imageR=images.ShieldR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.rang=self.stats["rang"]
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
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.game,self.side,
                         self.rang,self.dmg)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
    def take_damage(self,amount,source):
        if (source.x>self.x and self.facing==1) or (source.x<self.x and self.facing==-1):
            super().take_damage(amount/4,source)
        else:
            super().take_damage(amount,source)
##############################################################################
class Sprayer(clone):
    name="Sprayer"
    cost=clone_stats[name]["cost"]
    imageG=images.sprayerG
    imageR=images.sprayerR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.rang=self.stats["rang"]
        self.lastshot=0
    def shoot(self,a,dt):
        for e in a:
            bul=BasicGuyBullet(self.x,self.y+self.height/2,e[0],e[1],self.game,self.side,
                             self.rang,self.dmg)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
#########################################################################################
class MegaMixer(clone):
    name="MegaMixer"
    cost=clone_stats[name]["cost"]
    imageG=images.megamixerG
    imageR=images.megamixerR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.rang=self.stats["rang"]
        self.enemies=game.clones[1-self.side]
        self.succ=self.stats["succ"]
    def shoot(self,a,dt):
        for e in self.enemies:
            if e.exists and abs(e.x-self.x)<self.rang:
                if e.x<self.x:
                    e.x+=self.succ*dt
                else:
                    e.x-=self.succ*dt
        AOE_square(self,self.x,self.y+self.height/2,self.width/2,self.enemies,self.dmg*dt)
    def can_shoot(self):
        return False
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot([],dt)
####################################################################
class Smash(clone):
    name="Smash"
    cost=clone_stats[name]["cost"]
    imageG=images.SmashG
    imageR=images.SmashR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.lastshot=0
        self.enemies=game.clones[1-side]
        self.smashing="none"
        self.smashing_time=0
        self.knockback_x=self.stats["kbx"]
        self.knockback_y=self.stats["kby"]
        self.radius=self.stats["radius"]
        if side==0:
            self.spryte=pyglet.sprite.Sprite(self.imageG,10,100,batch=None,group=dudeg)
            self.left=pyglet.sprite.Sprite(images.SmashGL,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
            self.right=pyglet.sprite.Sprite(images.SmashGR,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
        else:
            self.spryte=pyglet.sprite.Sprite(self.imageR,10,100,batch=None,group=dudeg)
            self.left=pyglet.sprite.Sprite(images.SmashRL,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
            self.right=pyglet.sprite.Sprite(images.SmashRR,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
    def shoot(self,a,dt):
        if a[0]<=0:
            AOE_square(self,self.x-50,self.y+self.height/2,self.radius,self.enemies,self.dmg,
                       knockback_x=-self.knockback_x,knockback_y=self.knockback_y)
            self.smashing="left"
            self.sprite.batch=None
            if self.facing==1:
                self.sprite=self.left
                self.sprite.batch=self.game.batch
            else:
                self.sprite=self.right
                self.sprite.batch=self.game.batch
            self.sprite.scale_x=self.facing
        else:
            AOE_square(self,self.x+50,self.y+self.height/2,self.radius,self.enemies,self.dmg,
                       knockback_x=self.knockback_x,knockback_y=self.knockback_y)
            self.smashing="right"
            self.sprite.batch=None
            if self.facing==1:
                self.sprite=self.right
                self.sprite.batch=self.game.batch
            else:
                self.sprite=self.left
                self.sprite.batch=self.game.batch
            self.sprite.scale_x=self.facing
        self.smashing_time=0.3
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
    def move(self,dt):
        if self.smashing_time>0:
            self.smashing_time-=min(dt,self.smashing_time)
            if self.smashing_time==0:
                self.sprite.batch=None
                self.spryte.scale_x=self.sprite.scale_x
                self.sprite=self.spryte
                self.sprite.batch=self.game.batch
                self.smashing="none"
        super().move(dt)
    def die(self):
        self.sprite.batch=None
        self.sprite=self.spryte
        self.sprite.batch=None
        self.smashing="none"
        self.smashing_time=0
        super().die()
###########################################################################
class MachineGun(clone):
    name="MachineGun"
    cost=clone_stats[name]["cost"]
    imageG=images.gunmanG
    imageR=images.gunmanR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.rang=self.stats["rang"]
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
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.game,self.side,
                         self.rang,self.dmg)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
###########################################################################
class Tank(clone):
    name="Tank"
    cost=clone_stats[name]["cost"]
    imageG=images.tankG
    imageR=images.tankR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.rang=self.stats["rang"]
        self.lastshot=0
        self.eradius=self.stats["eradius"]
        self.dmg2=self.stats["dmg2"]
        self.enemies=game.clones[1-side]
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
        a=BazookaBullet(self.x,self.y+self.height/2,vx,vy,self.game,self.side,
                         self.rang,self.dmg,self.eradius)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
    def w(self):
        pass
    def knockback(self,a,b):
        super().knockback(a/4,b/3)
    def shoot2(self,dt):
        for e in self.enemies:
            if e.exists and e.x-e.width/2<self.x<e.x+e.width/2 and e.y<self.y+self.height/2<e.y+e.height:
                e.take_damage(self.dmg2*dt,self)
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot2(dt)
######################################################################################
class Engi(clone):
    name="Engi"
    cost=clone_stats[name]["cost"]
    imageG=images.engiG
    imageR=images.engiR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.lastshot=0
        self.turrets=[]
        self.aspd=self.stats["aspd"]
        self.radius=self.stats["radius"]
        self.damage=self.stats["dmg"]
        self.turret_spawned=False
        self.shoot,self.can_shoot=self.shoot1,self.can_shoot1
        self.enemies=game.clones[1-side]
    def shoot1(self,a,dt):
        self.turret_spawned=True
        Turret(self.game,self.side,self.turrets,self.x,self.y)
        self.shoot,self.can_shoot=self.shoot2,self.can_shoot2
    def can_shoot1(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd and not self.turret_spawned:
            self.lastshot=t
            return True
        return False

    def shoot2(self,a,dt):
        AOE_square(self,self.x,self.y+self.width//2,self.radius,self.enemies,self.damage)
    def can_shoot2(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False

    def start(self):
        super().start()
        self.shoot,self.can_shoot=self.shoot1,self.can_shoot1
        self.turret_spawned=False

class Grenade(Projectile):
    def __init__(self,x,y,vx,vy,game,side,rang,damage,radius):
        super().__init__(x,y,vx,vy,game,side,rang,damage,images.BazookaBullet)
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
    def explode(self,e=None):
        AOE_square(self,self.x,self.y,self.radius,self.enemies,self.damage)
        fire(self.x,self.y,0,0.5,self.game,growth=self.radius/150)
        super().die(0)
    def move(self,dt):
        self.x+=self.vx*dt
        ycap=-500
        for e in self.game.mapp.platforms:
            if self.y>e.y and self.vy<0 and rect_intersect(self.x,
                                                           self.y+self.vy*dt,
                                                           self.x,
                                                           self.y,
                                                           e.x,e.y+e.h,e.x+e.w,e.y+e.h):
                ycap=max(e.y+e.h,ycap)
        if not ycap==-500:
            self.y=2*ycap-self.vy*dt-self.y
            self.vy*=-0.7
            self.vx*=0.9
        else:
            self.y=self.y+self.vy*dt
            self.vy-=self.game.gravity*dt
        self.sprite.update(x=SPRITE_SIZE_MULT*(self.x-camx),y=SPRITE_SIZE_MULT*self.y)
        self.collide()
    def on_collision(self,e):
        pyglet.clock.unschedule(self.die)
        self.explode()
    def die(self,dt):
        self.explode()
        

class Turret(clone):
    name="Turret"
    imageG=images.turretG
    imageR=images.turretR
    def __init__(self,game,side,l2,x,y):
        super().__init__(game,side=side)
        self.l2=l2
        l2.append(self)
        self.lastshot=0
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.rang=self.stats["rang"]
        self.eradius=self.stats["eradius"]
        self.detect=self.stats["detect"]
        self.update_pos(x,y)
        self.exists=True
        self.active=False
        self.additional_images=[]
        self.enemies=game.clones[1-self.side]
    def start(self):
        self.schedule_die()
    def die(self):
        self.game.clones[self.side].remove(self)
        self.l2.remove(self)
        self.exists=False
        del self
    def move(self,dt):
        if self.exists:
            if self.can_shoot():
                self.aim_shoot()
            if self.move_locked and self.on_ground():
                self.move_locked=False
                self.vx=self.moving*self.spd
            self.exist_time+=dt
            self.x=self.x+self.vx*dt
            ycap=-500
            for e in self.game.mapp.platforms:
                if self.y>e.y and self.vy<0 and rect_intersect(self.x,
                                                                   self.y+self.vy*dt,
                                                                   self.x,
                                                                   self.y,
                                                                   e.x,e.y+e.h,e.x+e.w,e.y+e.h):
                    ycap=max(e.y+e.h,ycap)
            self.y=max(ycap,self.y+self.vy*dt)
            if not ycap==-500:
                self.vy=0
            else:
                self.vy-=self.game.gravity*dt
            if self.y<=-500:
                self.schedule_die()
            self.update_pos(self.x,self.y)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def aim_shoot(self):
        d=self.rang
        for e in self.enemies:
            if e.exists:
                de=abs(self.x-e.x)
                if de<=d:
                    d=de
                    target=e
        if d<self.detect:
            if target.x>self.x and self.facing==-1:
                self.facing=1
                self.sprite.scale_x=1
            elif target.x<self.x and self.facing==1:
                self.facing=-1
                self.sprite.scale_x=-1
            self.shoot([target.x-self.x,target.y+
                        target.height/2-self.y-self.height/2+100])
    def shoot(self,a):
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
        a=Grenade(self.x,self.y+self.height/2,vx,vy,self.game,self.side,
                         self.rang,self.dmg,self.eradius)
############################################################################
class MegaSmash(clone):
    name="MegaSmash"
    cost=clone_stats[name]["cost"]
    imageG=images.MSmashG
    imageR=images.MSmashR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.knockback_x=self.stats["kbx"]
        self.knockback_y=self.stats["kby"]
        self.lastshot=0
        self.enemies=game.clones[1-side]
        self.smashing="none"
        self.smashing_time=0
        self.radius=self.stats["radius"]
        if side==0:
            self.spryte=pyglet.sprite.Sprite(self.imageG,10,100,batch=None,group=dudeg)
            self.left=pyglet.sprite.Sprite(images.MSmashGL,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
            self.right=pyglet.sprite.Sprite(images.MSmashGR,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
        else:
            self.spryte=pyglet.sprite.Sprite(self.imageR,10,100,batch=None,group=dudeg)
            self.left=pyglet.sprite.Sprite(images.MSmashRL,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
            self.right=pyglet.sprite.Sprite(images.MSmashRR,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
    def shoot(self,a,dt):
        if a[0]<=0:
            AOE_square(self,self.x-40,self.y+self.height/3,self.radius,self.enemies,self.dmg,
                       knockback_x=-self.knockback_x,knockback_y=self.knockback_y)
            self.smashing="left"
            self.sprite.batch=None
            if self.facing==1:
                self.sprite=self.left
                self.sprite.batch=self.game.batch
            else:
                self.sprite=self.right
                self.sprite.batch=self.game.batch
            self.sprite.scale_x=self.facing
        else:
            AOE_square(self,self.x+40,self.y+self.height/3,self.radius,self.enemies,self.dmg,
                       knockback_x=self.knockback_x,knockback_y=self.knockback_y)
            self.smashing="right"
            self.sprite.batch=None
            if self.facing==1:
                self.sprite=self.right
                self.sprite.batch=self.game.batch
            else:
                self.sprite=self.left
                self.sprite.batch=self.game.batch
            self.sprite.scale_x=self.facing
        self.smashing_time=0.3
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
    def move(self,dt):
        if self.exists:
            if dt<1/55:
                fire(self.x-self.width/3,self.y+self.height*2.2/3,30,0.3,self.game,vy=200,growth=-0.10)
                fire(self.x+self.width/3,self.y+self.height*2.2/3,30,0.3,self.game,vy=200,growth=-0.10)
            if self.smashing_time>0:
                self.smashing_time-=min(dt,self.smashing_time)
                if self.smashing_time==0:
                    self.sprite.batch=None
                    self.spryte.scale_x=self.sprite.scale_x
                    self.sprite=self.spryte
                    self.sprite.batch=self.game.batch
                    self.smashing="none"
            super().move(dt)
    def die(self):
        self.sprite.batch=None
        self.sprite=self.spryte
        self.sprite.batch=None
        self.smashing="none"
        self.smashing_time=0
        super().die()
    def stomp(self,amount):
        if amount>100:
            earth(self.x,self.y-self.distance_from_ground(),
                  self.width*2/3,0.5,self.game,growth=amount/200)
            AOE_square(self,self.x,self.y-self.width/3,self.width*2/3,self.enemies,
                       amount,
                       knockback_y=amount/2)
#######################################################################
class FlameThrower(clone):
    name="FlameThrower"
    cost=clone_stats[name]["cost"]
    imageG=images.flameG
    imageR=images.flameR
    def __init__(self,game,side):
        super().__init__(game,side=side)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.aoey=self.stats["aoey"]
        self.aoex=self.stats["aoex"]
        self.lastshot=0
    def shoot(self,a,dt):
        AOE_rect(self,self.x,self.y+self.height//2-self.aoey//2,self.x+self.facing*self.aoex,
                 self.y+self.height//2+self.aoey//2,self.enemies,self.dmg)
        fire(self.x+self.width*2*self.facing/3,self.y+self.height*2/3,10,0.8,
             self.game,vx=400*self.facing,growth=0.3)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
########################################################################
possible_units=[BasicGuy,Mixer,Bazooka,Tele,Shield,Sprayer,MachineGun,Smash,Engi,
                Tank,MegaSmash,MegaMixer,FlameThrower]
possible_units.sort(key=get_cost)
