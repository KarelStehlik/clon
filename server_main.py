from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from imports import *
import maps
import clones_server as clones
from constants import *
import time
import serverchannels as channels
import socket
class player_channel(Channel):
    def start(self,side):
        self.side=side
        self.money=0
    def get_money(self,amount):
        self.money+=amount
        self.Send({"action":"update_money","money":self.money})
    def Network_stop(self,data):
        mt.game.current_clones[self.side].move_stop()
        channels.send_both({"action":"stop","side":self.side})
    def Network_A(self,data):
        mt.game.current_clones[self.side].a_start()
        channels.send_both({"action":"A","side":self.side})
    def Network_D(self,data):
        mt.game.current_clones[self.side].d_start()
        channels.send_both({"action":"D","side":self.side})
    def Network_jump(self,data):
        mt.game.current_clones[self.side].w()
        channels.send_both({"action":"jump","side":self.side})
    def Network_shoot(self,data):
        mt.game.current_clones[self.side].add_shoot(data["a"])
    def Network_chosen(self,data):
        mc.make_choice(self.side,data["choice"],self.money)
mappNum=0
class cw_server(Server):
    channelClass = player_channel
    def Connected(self, channel, addr):
        n=len(channels.cn)
        channel.start(n)
        channel.Send({"action":"assign_side","s":n})
        if n<2:
            channels.cn+=[channel]
            n+=1
        if n==2:
            global mappNum
            mappNum=random.randint(0,len(maps.maps)-1)
            channels.send_both({"action":"start",
                                "mapp":mappNum})

srvr=cw_server(localaddr=("192.168.1.132",5071))

class mode_building():
    def __init__(self,**kw):
        pass

class mapp():
    def __init__(self,mapp):
        self.platforms=mapp
class mode_testing():
    def __init__(self,**kw):
        if "mapp" in kw:
            self.mapp=maps.maps[kw["mapp"]]
        else:
            self.mapp=random.choice(maps.maps)
        self.mapp=mapp(self.mapp)
        self.gravity=1000
        self.running=False
        self.game=clones.Game(self.mapp,self.gravity)
        self.summon_clones(0,1)
        self.end_scheduled=False
    def end_round(self,dt):
        self.end_scheduled=False
        self.running=False
        global current_mode
        current_mode=mode_choosing()
        self.game.end_round()
    def summon_clones(self,c0,c1):
        self.game.summon_clones(c0,c1)
        self.running=True
    def tick(self,dt):
        if self.running:
            self.game.tick(dt)
            if ((not self.game.current_clones[1].exists) or (not self.game.current_clones[0].exists)) and not self.end_scheduled:
                pyglet.clock.schedule_once(self.end_round,5)
                self.end_scheduled=True

class mode_choosing():
    def __init__(self):
        self.choices=[-1,-1]
        global mc
        mc=self
        self.active=True
    def make_choice(self,side,c,money):
        if 0<=c<=len(clones.possible_units) and clones.possible_units[c].cost<=money:
            self.choices[side]=int(c)
            if self.active and not self.choices[1-side] == -1:
                global current_mode,mt
                channels.cn[0].get_money(-clones.possible_units[self.choices[0]].cost)
                channels.cn[1].get_money(-clones.possible_units[self.choices[1]].cost)
                current_mode=mt
                self.active=False
                current_mode.summon_clones(self.choices[0],self.choices[1])
    def tick(self,dt):
        pass

def main_loop(dt):
    srvr.Pump()
    for e in channels.cn:
        e.Pump()
    current_mode.tick(dt)

while len(channels.cn)<2:
    srvr.Pump()
mc=mode_choosing()
mt=mode_testing(mapp=mappNum)
current_mode=mt
pyglet.clock.schedule_interval(main_loop,1.0/60)
print("starting game")
while True:
    pyglet.clock.tick()
