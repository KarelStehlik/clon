from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from imports import *
import maps
import clones_server as clones
from constants import *
import time
import serverchannels as channels

class player_channel(Channel):
    def start(self,side):
        self.side=side
    def Network_stop(self,data):
        current_mode.current_clones[self.side].move_stop()
        channels.send_both({"action":"stop","side":self.side})
    def Network_A(self,data):
        current_mode.current_clones[self.side].a_start()
        channels.send_both({"action":"A","side":self.side})
    def Network_D(self,data):
        current_mode.current_clones[self.side].d_start()
        channels.send_both({"action":"D","side":self.side})
    def Network_jump(self,data):
        current_mode.current_clones[self.side].w()
        channels.send_both({"action":"jump","side":self.side})
    def Network_shoot(self,data):
        current_mode.current_clones[self.side].add_shoot(data["a"])

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
            channels.send_both({"action":"start",
                                "mapp":random.randint(0,len(maps.maps)-1)})

srvr=cw_server()
print(srvr.addr)

class mapp():
    def __init__(self,mapp):
        self.platforms=mapp
class mode_testing():
    def __init__(self,**kw):
        if "map" in kw:
            self.mapp=kw["map"]
        else:
            self.mapp=random.choice(maps.maps)
        self.mapp=mapp(self.mapp)
        self.gravity=1000
        self.clones=[[],[]]
        self.bullets=[]
        self.current_clones=[None,None]
        self.running=False
        self.summon_clones(0,1)
    def end_round(self):
        self.running=False
        self.current_clones[0].die()
        self.current_clones[1].die()
        channels.send_both({"action":"endround","log0":self.current_clones[0].log,
                   "log1":self.current_clones[1].log})
        self.summon_clones(1,1)
    def summon_clones(self,c0,c1):
        self.current_clones[0]=(clones.possible_units)[c0](self.mapp,
                                                            self.clones,
                                                            self.bullets,
                                                            0)
        self.current_clones[1]=(clones.possible_units)[c1](self.mapp,
                                                            self.clones,
                                                            self.bullets,
                                                            1)
        channels.send_both({"action":"summon","c":c0,"s":0})
        channels.send_both({"action":"summon","c":c1,"s":1})
        channels.send_both({"action":"start_round"})
        for e in self.clones[0]:
            e.start()
        for e in self.clones[1]:
            e.start()
        self.running=True
    def tick(self,dt):
        if self.running:
            for e in self.clones[0]:
                e.move(dt)
                e.vy-=self.gravity*dt
            for e in self.clones[1]:
                e.move(dt)
                e.vy-=self.gravity*dt
            for e in self.bullets:
                e.move(dt)
            if (not self.current_clones[1].exists) or (not self.current_clones[0].exists):
                self.end_round()

while len(channels.cn)<2:
    srvr.Pump()
channels.send_both({"action":"start_game"})
current_mode=mode_testing()
pyglet.clock.schedule_interval(current_mode.tick,1.0/60)
print("cn")
t=1
while True:
    t+=1
    if t%3000==0:
        t=0
    srvr.Pump()
    for e in channels.cn:
        e.Pump()
    pyglet.clock.tick()
