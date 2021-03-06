import images
import pyglet
import time
import numpy as np
import math
import random
from constants import *
import serverchannels as channels
dudeg=pyglet.graphics.OrderedGroup(2)
ID=0
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

if __name__=="__main__":
    print(clone_stats)

class Game():
    def __init__(self,mapp,gravity):
        self.clones=[[],[]]
        self.current_clones=[None,None]
        self.mapp=mapp
        self.gravity=gravity
        self.bullets=[]
        self.deadclones=[]
        channels.cn[1].get_money(100)
        channels.cn[0].get_money(100)
        self.money_per_round=100
        self.round=0
    def add_base_defense(self,n,side,x,y):
        base_defenses[n](self,side,x=x,y=y,AI=True)
    def summon(self,n,side):
        self.current_clones[side]=possible_units[n](self,
                                                    side)
    def tick(self,dt):
        for i in range(len(self.deadclones)):
            deed=self.deadclones.pop(0)
            deed.die()
        for e in self.clones[0]:
            e.move(dt)
        for e in self.clones[1]:
            e.move(dt)
        for e in self.bullets:
            e.move(dt)
        channels.send_both({"action":"update",
                                "hp0":self.current_clones[0].hp,
                                "hp1":self.current_clones[1].hp,
                                "x0":self.current_clones[0].x,
                                "y0":self.current_clones[0].y,
                                "x1":self.current_clones[1].x,
                                "y1":self.current_clones[1].y})
    def end_round(self):
        self.current_clones[0].die()
        self.current_clones[1].die()
        channels.cn[1].get_money(self.money_per_round)
        channels.cn[0].get_money(self.money_per_round)
        self.money_per_round=min(self.money_per_round+100,2000)
        channels.send_both({"action":"endround","log0":self.current_clones[0].log,
                   "log1":self.current_clones[1].log})
    def summon_clones(self,c0,c1):
        self.summon(c0,0)
        self.summon(c1,1)
        channels.send_both({"action":"summon","c":c0,"s":0})
        channels.send_both({"action":"summon","c":c1,"s":1})
        self.start_round()
    def start_round(self):
        channels.send_both({"action":"start_round"})
        self.round+=1
        self.deadclones=[]
        for e in self.clones[0]:
            e.start()
        for e in self.clones[1]:
            e.start()
def rect_intersect(ax1,ay1,ax2,ay2,bx1,by1,bx2,by2):
    return max(ax1,ax2)>=min(bx1,bx2) and  min(ax1,ax2)<=max(bx1,bx2) and max(ay1,ay2)>=min(by1,by2) and  min(ay1,ay2)<=max(by1,by2)
def take_second(l):
    return l[1]
class clone():
    def __init__(self,game,AI=False,x=None,y=None,**kwargs):
        global ID
        stats=clone_stats[self.name]
        self.stats=stats
        self.ID=ID
        ID+=1
        self.side=kwargs["side"]
        self.maxhp=stats["hp"]
        self.hp=self.maxhp
        self.height=stats["height"]
        self.width=stats["width"]
        self.spd=stats["spd"]
        self.jump=stats["jump"]
        self.rang=stats["rang"]
        self.mapp=game.mapp
        self.active=not AI
        self.exists=True
        self.vx=self.vy=0
        self.log=[]
        self.log_completed=0
        self.exist_time=0
        self.lastshot=0
        game.clones[self.side].append(self)
        self.l=game.clones
        self.facing=1
        if x==None:
            if self.side==0:
                self.x=10
            else:
                self.x=1270
            self.y=100
        else:
            self.x,self.y=x,y
        self.baseX,self.baseY=self.x,self.y
        self.moving=0
        self.move_locked=False
        self.shoot_queue=[]
        self.game=game
        self.enemies=self.l[1-self.side]
        self.AI=AI
        if AI:
            self.detect=stats["detect"]
    def ability(self,ID,value):
        if self.exists and self.active:
            self.log.append(["ability",self.exist_time,ID,value])
            channels.send_both({"action":"ability","side":self.side,"ID":ID,"value":value})
    def add_shoot(self,a):
        self.shoot_queue.append(a)
    def can_shoot(self):
        return False
    def schedule_die(self):
        if self.exists:
            self.exists=False
            self.game.deadclones.append(self)
    def start(self):
        self.x,self.y=self.baseX,self.baseY
        self.hp=self.maxhp
        self.exists=True
        self.log_completed=0
        self.exist_time=0
        self.lastshot=0
        self.vx=self.vy=0
        if self.AI:
            self.log=[]
    def take_damage(self,amount,source):
        if self.exists:
            self.hp-=amount
            if self.hp<=0:
                self.schedule_die()
    def on_ground(self):
        for e in self.mapp.platforms:
            if self.y==e.y+e.h and e.x<self.x<e.x+e.w:
                return True
        return False
    def a_start(self):
        if self.exists:
            if self.active:
                self.log.append(["a",self.exist_time])
            self.facing=self.moving=-1
            if not self.move_locked:
                self.vx=-self.spd
    def move_stop(self):
        if self.exists:
            if self.active:
                self.log.append(["stop",self.exist_time])
            self.moving=0
            if not self.move_locked:
                self.vx=0
    def d_start(self):
        if self.exists:
            if self.active:
                self.log.append(["d",self.exist_time])
            self.facing=self.moving=1
            if not self.move_locked:
                self.vx=self.spd
    def w(self):
        if self.exists:
            if self.active:
                self.log.append(["w",self.exist_time])
            if self.on_ground():
                self.vy=self.jump
    def knockback(self,x,y):
        if self.exists:
            self.y+=1
            self.vx+=x
            self.vy+=y
            self.move_locked=True
    def AI_move(self):
        d=self.detect
        for e in self.enemies:
            if e.exists:
                de=abs(self.x-e.x)
                if de<d:
                    d=de
                    target=e
        if d<self.detect:
            if self.can_shoot():
                self.shoot([target.x-self.x,target.y+
                            target.height/2-self.y-self.height/2],0)
            if abs(self.x-target.x)>self.rang:
                if target.x>self.x:
                    self.d_start()
                else:
                    self.a_start()
            else:
                self.move_stop()
            if target.y>self.y:
                self.w()
        else:
            self.move_stop()
    def move(self,dt):
        if self.exists:
            if self.on_ground():
                if self.move_locked:
                    self.move_locked=False
                self.vx=self.moving*self.spd
            self.exist_time+=dt
            if self.AI:
                self.AI_move()
            else:
                if self.active:
                    if len(self.shoot_queue)>0 and self.can_shoot():
                        self.shoot(self.shoot_queue.pop(0),0)
                else:
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
                            elif e[0]=="ability":
                                self.ability(e[2],e[3])
                        else:
                            break
            self.x=self.x+self.vx*dt
            ycap=-500
            for e in self.mapp.platforms:
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
    def stomp(self,amount):
        pass
    def shoot(self,a,dt=0):
        pass
    def die(self):
        if self.active:
            self.log.append(["die",self.exist_time+0.1])
            self.active=False
            self.log.sort(key=take_second)
        self.moving=self.vy=self.vx=0
        self.exists=False
class Projectile():
    def __init__(self,x,y,vx,vy,enemies,rang,damage,game):
        self.x,self.y,self.vx,self.vy=x,y,vx,vy
        self.enemies=enemies
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
    def __init__(self,x,y,vx,vy,enemies,rang,damage,game):
        super().__init__(x,y,vx,vy,enemies,rang,damage,game)
    def on_collision(self,e):
        e.take_damage(self.damage,self)
        pyglet.clock.unschedule(self.die)
        self.die(0)
class BasicGuy(clone):
    name="BasicGuy"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.game)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
###########################################################################################################
class Mixer(clone):
    name="Mixer"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
    def shoot(self,a,dt):
        AOE_square(self,self.x,self.y+self.height*2/3,self.width/2,self.enemies,self.dmg*dt)
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot([],dt)
#########################################################################################################
class Bazooka(clone):
    name="Bazooka"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.eradius=self.stats["eradius"]
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
        a=BazookaBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.game,self.eradius)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
class BazookaBullet(Projectile):
    def __init__(self,x,y,vx,vy,enemies,rang,damage,game,radius):
        super().__init__(x,y,vx,vy,enemies,rang,damage,game)
        self.radius=radius
    def on_collision(self,e):
        AOE_square(self,self.x,self.y,self.radius,self.enemies,self.damage)
        pyglet.clock.unschedule(self.die)
        self.die(0)
##################################################################################################################
class Tele(clone):
    name="Tele"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.radius=self.stats["radius"]
        self.port_speed=self.stats["port_speed"]
        self.phase=255
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
        self.y=max(self.y+a[1],50)
        self.x+=a[0]
        self.phase=0
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def move(self,dt):
        if (not self.phase==255) and self.exists:
            self.exist_time+=dt
            self.phase=min(self.phase+self.port_speed*dt,255)
            if self.phase==255:
                AOE_square(self,self.x,self.y,self.radius,self.enemies,self.dmg)
        else:
            super().move(dt)
    def die(self):
        self.phase=255
        super().die()
#####################################################################
class Shield(clone):
    name="Shield"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.game)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def take_damage(self,amount,source):
        if (source.x>self.x and self.facing==1) or (source.x<self.x and self.facing==-1):
            super().take_damage(amount/4,source)
        else:
            super().take_damage(amount,source)
##########################################################################################################################################
class Sprayer(clone):
    name="Sprayer"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
    def shoot(self,a,dt):
        if self.active:
            bullet_data=[]
            for i in range(500):
                x=random.random()*random.choice([-1,1])
                y=random.random()*random.choice([-1,1])
                v=random.randint(int(self.bspd/1.1),self.bspd)
                if x==0:
                    vx=v
                    vy=0
                else:
                    vx=v/math.sqrt(y**2/x**2+1)
                    if x<0:
                        vx*=-1
                    vy=vx*y/x
                bul=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                                     self.rang,self.dmg,self.game)
                bullet_data.append([vx,vy])
            channels.send_both({"action":"shoot","a":bullet_data,"side":self.side})
            self.log.append(["shoot",self.exist_time,bullet_data])
        else:
            for e in a:
                bul=BasicGuyBullet(self.x,self.y+self.height/2,e[0],e[1],self.l[1-self.side],
                                     self.rang,self.dmg,self.game)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
###########################################################
class MegaMixer(clone):
    name="MegaMixer"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.succ=self.stats["succ"]
        self.radius=self.stats["radius"]
    def shoot(self,a,dt):
        for e in self.enemies:
            if e.exists and abs(e.x-self.x)<self.radius:
                if e.x<self.x:
                    e.x+=self.succ*dt
                else:
                    e.x-=self.succ*dt
        AOE_square(self,self.x,self.y+self.height/2,self.width/2,self.enemies,self.dmg*dt)
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot([],dt)
################################################################
class Smash(clone):
    name="Smash"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.knockback_x=self.stats["kbx"]
        self.knockback_y=self.stats["kby"]
        self.radius=self.stats["radius"]
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
        if a[0]<=0:
            AOE_square(self,self.x-50,self.y+self.height/2,self.radius,self.enemies,self.dmg,
                       knockback_x=-self.knockback_x,knockback_y=self.knockback_y)
        else:
            AOE_square(self,self.x+50,self.y+self.height/2,self.radius,self.enemies,self.dmg,
                       knockback_x=self.knockback_x,knockback_y=self.knockback_y)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
############################################################################3
class MachineGun(clone):
    name="MachineGun"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.game)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
#################################################################################
class Tank(clone):
    name="Tank"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.eradius=self.stats["eradius"]
        self.dmg2=self.stats["dmg2"]
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
        a=BazookaBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.game,self.eradius)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def shoot2(self,dt):
        for e in self.enemies:
            if e.exists and e.x-e.width/2<self.x<e.x+e.width/2 and e.y<self.y+self.height/2<e.y+e.height:
                e.take_damage(self.dmg2*dt,self)
    def w(self):
        pass
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot2(dt)
    def knockback(self,a,b):
        super().knockback(a/4,b/3)
################################################################################
class Engi(clone):
    name="Engi"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.aspd=self.stats["aspd"]
        self.radius=self.stats["radius"]
        self.damage=self.stats["dmg"]
        self.turret_spawned=False
        self.shoot,self.can_shoot=self.shoot1,self.can_shoot1
    def shoot1(self,a,dt):
        self.turret_spawned=True
        Turret(self.game,self.side,self.x,self.y)
        self.shoot,self.can_shoot=self.shoot2,self.can_shoot2
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
        self.turret_spawned=False
        self.shoot,self.can_shoot=self.shoot1,self.can_shoot1

class Grenade(Projectile):
    def __init__(self,x,y,vx,vy,enemies,rang,damage,game,radius):
        super().__init__(x,y,vx,vy,enemies,rang,damage,game)
        self.radius=radius
    def explode(self,e=None):
        AOE_square(self,self.x,self.y,self.radius,self.enemies,self.damage)
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
        self.collide()
    def on_collision(self,e):
        pyglet.clock.unschedule(self.die)
        self.explode()
    def die(self,dt):
        self.explode()

class Turret(clone):
    name="Turret"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,x,y,**kw):
        super().__init__(game,side=side,AI=True)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.bspd=self.stats["bspd"]
        self.eradius=self.stats["eradius"]
        self.x,self.y=x,y
        self.exists=True
    def start(self):
        self.schedule_die()
    def die(self):
        self.l[self.side].remove(self)
        self.exists=False
        del self
    def take_damage(self,amount,source):
        if self.exists:
            self.hp-=amount
            if self.hp<=0:
                self.schedule_die()
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False                
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
        a=Grenade(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.game,self.eradius)
############################################################################
class MegaSmash(clone):
    name="MegaSmash"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.knockback_x=self.stats["kbx"]
        self.knockback_y=self.stats["kby"]
        self.radius=self.stats["radius"]
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
        if a[0]<=0:
            AOE_square(self,self.x-40,self.y+self.height/3,self.radius,self.enemies,self.dmg,
                       knockback_x=-self.knockback_x,knockback_y=self.knockback_y)
        else:
            AOE_square(self,self.x+40,self.y+self.height/3,self.radius,self.enemies,self.dmg,
                       knockback_x=self.knockback_x,knockback_y=self.knockback_y)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def stomp(self,amount):
        if amount>100:
            AOE_square(self,self.x,self.y-self.width/3,self.width*2/3,self.enemies,
                       amount,
                       knockback_y=amount/2)
            if self.active:
                channels.send_both({"action":"stomp",
                                    "amount":amount,"side":self.side})
#################################################################################3
class FlameThrower(clone):
    name="FlameThrower"
    cost=clone_stats[name]["cost"]
    base_cost=clone_stats[name]["base_cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.aoex=self.stats["aoex"]
        self.aoey=self.stats["aoey"]
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
        AOE_rect(self,self.x,self.y+self.height//2-self.aoey//2,self.x+self.facing*self.aoex,
                 self.y+self.height//2+self.aoey//2,self.enemies,self.dmg)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
##################################################################################################
class Jetpack(clone):
    name="Jetpack"
    cost=clone_stats[name]["cost"]
    def __init__(self,game,side,**kw):
        super().__init__(game,side=side,**kw)
        self.dmg=self.stats["dmg"]
        self.aspd=self.stats["aspd"]
        self.radius=self.stats["radius"]
        self.boost=self.stats["boost"]
        self.flycd=self.stats["flycd"]
        self.turnspeed=self.stats["turnspeed"]
        self.maxvx=self.stats["maxvx"]
        self.vydamp=self.stats["vydamp"]
        self.maxfuel=self.fuel=self.stats["maxfuel"]
        self.fuelregen=self.stats["fuelregen"]
        self.angle=math.pi/2
        self.lastused1=0
    def ability(self,ID,value):
        if ID==0 and self.can_use_1():
            super().ability(ID,value)
            self.lastused1=self.exist_time
            a=Grenade(self.x,self.y,0,10,self.l[1-self.side],
                        self.rang,self.dmg,self.game,self.radius)
            a.vx=self.vx
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
            self.fuel-=1
        if a==[0,0]:
            newangle=0
        elif a[0]==0:
            newangle=(a[1]>0)*math.pi
        elif a[0]>0:
            newangle=math.atan(a[1]/a[0])
        elif a[0]<0:
            newangle=math.atan(a[1]/a[0])+math.pi
        newangle%=2*math.pi
        if newangle<self.angle:
            if self.angle-newangle>math.pi:
                self.angle+=min(self.turnspeed,newangle+2*math.pi-self.angle)
            else:
                self.angle-=min(self.turnspeed,self.angle-newangle)
        else:
            if newangle-self.angle>math.pi:
                self.angle-=min(self.turnspeed,self.angle+2*math.pi-newangle)
            else:
                self.angle+=min(self.turnspeed,newangle-self.angle)
        self.angle%=2*math.pi
        self.knockback(math.cos(self.angle)*self.boost,
                       math.sin(self.angle)*self.boost*self.vydamp)
        self.vx=min(self.maxvx,max(-self.maxvx,self.vx))
    def can_shoot(self):
        if self.fuel<1 or not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.flycd:
            self.lastshot=t
            return True
        return False
    def can_use_1(self):
        if not self.exists:
            return False
        if not self.active:
            return True
        t=self.exist_time
        if t-self.lastused1>self.aspd:
            self.lastused1=t
            return True
        return False
    def move(self,dt):
        super().move(dt)
        self.fuel=min(self.fuel+self.fuelregen*dt,self.maxfuel)
#################################################################################################
possible_units=[BasicGuy,Mixer,Bazooka,Tele,Shield,Sprayer,MachineGun,Smash,Engi,
                Tank,MegaSmash,MegaMixer,FlameThrower,Jetpack]
possible_units.sort(key=get_cost)

base_defenses=[BasicGuy,Mixer,Bazooka,Tele,Shield,MachineGun,Smash,Engi,
                Tank,MegaSmash,MegaMixer,FlameThrower]
