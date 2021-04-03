from PodSixNet.Connection import connection,ConnectionListener
from imports import *
import maps
import clones_client as clones
from constants import *
import multiprocessing as mpc
connection.DoConnect(('127.0.0.1', 5071))
class MyNetworkListener(ConnectionListener):
    def __init__(self,*args,**kwargs):
        super().__init__()
        self.start=False
    def Network_assign_side(self,data):
        #print(data["action"])
        global side
        side=data["s"]
    def Network_start(self,data):
        #print(data["action"])
        self.start=True
        place.bb=place.current_mode=mode_base_building(place,place.mainBatch,mapp=data["mapp"])
    def Network_BB_finish(self,data):
        place.bb.finish()
    def Network_stop(self,data):
        #print(data["action"])
        place.main.game.current_clones[data["side"]].move_stop()
    def Network_A(self,data):
        #print(data["action"])
        place.main.game.current_clones[data["side"]].a_start()
    def Network_D(self,data):
        #print(data["action"])
        place.main.game.current_clones[data["side"]].d_start()
    def Network_jump(self,data):
        #print(data["action"])
        place.main.game.current_clones[data["side"]].w()
    def Network_ability(self,data):
        #print(data["action"])
        place.main.game.current_clones[data["side"]].ability(data["ID"],data["value"])
    def Network_summon(self,data):
        #print(data["action"])
        place.main.summon_clone(data["c"],data["s"])
    def Network_start_round(self,data):
        #print(data["action"])
        place.cc.end()
        place.main.start_round()
    def Network_endround(self,data):
        #print(data["action"])
        place.main.game.current_clones[0].die()
        place.main.game.current_clones[1].die()
        place.main.game.current_clones[0].log=data["log0"]
        place.main.game.current_clones[1].log=data["log1"]
        place.cc.start(side)
    def Network_shoot(self,data):
        #print(data["action"])
        place.main.game.current_clones[data["side"]].shoot(data["a"],0)
    def Network_stomp(self,data):
        place.main.game.current_clones[data["side"]].stomp(data["amount"])
    def Network_update(self,data):
        #print(data["action"])
        place.main.game.current_clones[0].update_health(data["hp0"])
        place.main.game.current_clones[1].update_health(data["hp1"])
        place.main.game.current_clones[0].update_pos(data["x0"],data["y0"])
        place.main.game.current_clones[1].update_pos(data["x1"],data["y1"])
    def Network_update_money(self,data):
        place.money=data["money"]
    def Network_place_thing(self,data):
        place.bb.place_thing(data["c"],data["side"],data["x"],data["y"])
nwl=MyNetworkListener()
class mode():
    def __init__(self,win,batch):
        self.batch=batch
        self.mousex=self.mousey=0
        self.win=win
    def mouse_move(self,x, y, dx, dy):
        self.mousex=x
        self.mousey=y
    def mouse_drag(self,x, y, dx, dy, button, modifiers):
        self.mouse_move(x,y,dx,dy)
    def tick(self,dt):
        self.win.switch_to()
        self.draw_all()
        self.win.flip()
    def draw_all(self):
        self.win.clear()
        self.batch.draw()
    def key_press(self,symbol,modifiers):
        pass
    def key_release(self,symbol,modifiers):
        pass
    def resize(self,width,height):
        pass
    def mouse_press(self,x,y,button,modifiers):
        pass
    def mouse_release(self,x,y,button,modifiers):
        pass
    def mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass
def rect_intersect(ax1,ay1,ax2,ay2,bx1,by1,bx2,by2):
    return ax1<=bx2 and bx1<=ax2 and ay1<=by2 and by1<=ay2
class mode_choosing(mode):
    def __init__(self,win,batch,**kwargs):
        super().__init__(win,batch)
        self.ccgroup1=pyglet.graphics.OrderedGroup(3)
        self.ccgroup2=pyglet.graphics.OrderedGroup(4)
        self.ccgroup3=pyglet.graphics.OrderedGroup(5)
        self.win=win
        self.batch=batch
        self.cframes=[]
        self.imgs=[]
        self.moved=0
        self.select=pyglet.text.Label(x=-500,multiline=True,width=images.cloneFrame.width,
                                y=-500,color=(255,255,0,255),
                                batch=self.batch,group=self.ccgroup3,font_size=int(30*SPRITE_SIZE_MULT),
                                anchor_x="center",align="center",anchor_y="bottom")
    def start(self,side):
        self.select.batch=self.batch
        self.select.x=-500
        self.select.y=-500
        self.win.current_mode=self
        i=0
        w=images.cloneFrame.width
        for e in clones.possible_units:
            a=pyglet.sprite.Sprite(images.cloneFrame,x=(i*w+30),
                                   y=30*SPRITE_SIZE_MULT,batch=self.batch,group=self.ccgroup1)
            if side==1:
                b=pyglet.sprite.Sprite(e.imageR,x=(i*w+30+w*e.imageR.anchor_x/e.imageG.width),
                                       y=53*SPRITE_SIZE_MULT,batch=self.batch,group=self.ccgroup2)
            else:
                b=pyglet.sprite.Sprite(e.imageG,x=(i*w+30+w*e.imageG.anchor_x/e.imageG.width),
                                       y=53*SPRITE_SIZE_MULT,batch=self.batch,group=self.ccgroup2)
            b.scale=(w/e.imageG.width)*0.8
            self.cframes.append(a)
            self.imgs.append(b)
            c=pyglet.text.Label(x=int(i*w+w/2+30*SPRITE_SIZE_MULT),
                                y=490*SPRITE_SIZE_MULT,text=str(int(e.cost)),color=(255,255,0,255),
                                batch=self.batch,group=self.ccgroup3,font_size=int(40*SPRITE_SIZE_MULT),
                                anchor_x="center")
            self.imgs.append(c)
            i+=1
    def mouse_press(self,x,y,button,modifiers):
        i=0
        w=images.cloneFrame.width
        for e in self.cframes:
            if e.x<x<e.x+e.width and e.y<y<e.y+e.height:
                self.select.x=int((i+self.moved)*w+w/2+30*SPRITE_SIZE_MULT)
                self.select.y=50*SPRITE_SIZE_MULT
                if self.win.money>=clones.possible_units[i].cost:
                    connection.Send({"action":"chosen","choice":i})
                    self.select.text="selected"
                else:
                    self.select.text="not enough money"
                return
            i+=1
    def end(self):
        self.win.currentMode=self.win.main
        for e in self.cframes:
            e.delete()
            del e
        for e in self.imgs:
            e.delete()
            del e
        self.cframes=[]
        self.imgs=[]
        self.select.batch=None
        self.moved=0
    def key_press(self,symbol,modifiers):
        if symbol in [key.RIGHT,key.D]:
            w=self.cframes[0].width
            for e in self.cframes+self.imgs+[self.select]:
                e.x-=w
            self.moved-=1
        elif symbol in [key.LEFT,key.A]:
            w=self.cframes[0].width
            for e in self.cframes+self.imgs+[self.select]:
                e.x+=w
            self.moved+=1

class mappClass():
    def __init__(self,inp,batch):
        self.platforms=[]
        for e in inp:
            self.platforms.append(e.batch(batch))
    def update(self,camx):
        for e in self.platforms:
            e.pic.x=(e.x-camx)*SPRITE_SIZE_MULT
class mode_testing(mode):
    def __init__(self,win,batch,mapp,game):
        super().__init__(win,batch)
        global side
        self.side=side
        self.camx=0
        self.batch=batch
        bg=pyglet.graphics.OrderedGroup(0)
        self.background=pyglet.sprite.Sprite(images.Background,x=0,y=0,group=bg,batch=batch)
        self.background.scale_x=win.width*2/self.background.width
        self.background.scale_y=win.height/self.background.height
        self.half_bg_width=self.background.width//2
        self.bg_shift=0
        self.mapp=mapp
        self.total_time=0
        self.game=game
        self.time_left=30
        self.time_indicator=pyglet.text.Label(x=20,y=SCREEN_HEIGHT-20,
                            text=str(int(self.time_left)),color=(255,255,255,255),
                            batch=self.batch,group=clones.projectileg,font_size=int(40*SPRITE_SIZE_MULT),
                            anchor_x="left",anchor_y="top")
    def start_round(self):
        self.win.current_mode=self
        self.game.start_round()
        self.time_left=self.game.round*TIME_PER_WAVE+TIME_BASELINE
    def summon_clone(self,n,side):
        self.game.summon(n,side)
    def mouse_drag(self,x, y, dx, dy, button, modifiers):
        self.mouse_move(x,y,dx,dy)
    def tick(self,dt):
        self.time_left-=dt
        self.time_indicator.text=str(int(self.time_left)+1)
        if not self.game.current_clones[self.side]==None:
            self.total_time+=dt
            self.camx=self.game.get_vpoint()
            cx=self.camx
            if self.background.x>=0:
                self.bg_shift-=1
            elif self.background.x<=-self.half_bg_width:
                self.bg_shift+=1
            clones.camx=cx
            self.background.x=-cx+self.bg_shift*self.half_bg_width
            self.mapp.update(cx)
            self.game.tick(dt,self.win.mouseheld,self.mousex,self.mousey)
            self.game.graphics_update(1/60)
            super().tick(dt)
    def key_press(self,symbol,modifiers):
        if symbol==key.A:
            connection.Send({"action": "A"})
        if symbol==key.D:
            connection.Send({"action": "D"})
        if symbol==key.W:
            connection.Send({"action": "jump"})
        else:
            self.game.key_press(symbol,self.side)
    def key_release(self,symbol,modifiers):
        if (symbol==key.A and not self.win.keys[key.D]) or (symbol==key.D and not self.win.keys[key.A]):
            connection.Send({"action": "stop"})
        elif symbol==key.A:
            connection.Send({"action": "D"})
        elif symbol==key.D:
            connection.Send({"action": "A"})

class mode_base_building(mode):
    def __init__(self,win,batch,mapp):
        super().__init__(win,batch)
        global side
        self.side=side
        self.gravity=GRAVITY
        bg=pyglet.graphics.OrderedGroup(0)
        self.mapp=mappClass(maps.maps[mapp],batch)
        self.game=clones.Game(self.mapp,self.batch,connection,self.gravity,side=self.side)
        self.camx=0
        self.selected=0
        self.money=BASE_BUILD_MONEY
        self.selected=0
        self.bg_red=batch.add(4,pyglet.gl.GL_QUADS,bg,
                                    ("v2i",[SCREEN_WIDTH//2,0,10000,0,10000,SCREEN_HEIGHT,
                                            SCREEN_WIDTH//2,SCREEN_HEIGHT]),
                                    ("c3B",[255,0,0,0,0,0,0,0,0,255,0,0]),
                                    )
        self.bg_blue=batch.add(4,pyglet.gl.GL_QUADS,bg,
                                    ("v2i",[SCREEN_WIDTH//2,0,-10000,0,-10000,SCREEN_HEIGHT,
                                            SCREEN_WIDTH//2,SCREEN_HEIGHT]),
                                    ("c3B",[0,0,255,0,0,0,0,0,0,0,0,255]),
                                    )
        if self.side==0:
            self.cselect=pyglet.sprite.Sprite(clones.base_defenses[self.selected].imageG,
                                              x=100*SPRITE_SIZE_MULT,y=20*SPRITE_SIZE_MULT,
                                              group=clones.dudeg,batch=self.batch)
        else:
            self.cselect=pyglet.sprite.Sprite(clones.base_defenses[self.selected].imageR,
                                              x=100*SPRITE_SIZE_MULT,y=20*SPRITE_SIZE_MULT,
                                              group=clones.dudeg,batch=self.batch)
        self.cselect.scale=3
        self.cselect_cost=pyglet.text.Label(x=100*SPRITE_SIZE_MULT,y=20*SPRITE_SIZE_MULT,
                            text=str(int(clones.base_defenses[self.selected].base_cost)),color=(255,255,0,255),
                            batch=self.batch,group=clones.projectileg,font_size=int(40*SPRITE_SIZE_MULT),
                            anchor_x="center")
        self.money_label=pyglet.text.Label(x=SCREEN_WIDTH-20,y=SCREEN_HEIGHT-20,
                            text=str(self.money),color=(255,255,0,255),
                            batch=self.batch,group=clones.projectileg,font_size=int(40*SPRITE_SIZE_MULT),
                            anchor_x="right",anchor_y="top")
        self.win.money_label.batch=None
        self.update_camx(SCREEN_WIDTH//2 if self.side==1 else -SCREEN_WIDTH//2)
    def mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.selected+=int(scroll_y)
        self.selected=self.selected%len(clones.base_defenses)
        self.cselect.delete()
        if self.side==0:
            self.cselect=pyglet.sprite.Sprite(clones.base_defenses[self.selected].imageG,
                                              x=100*SPRITE_SIZE_MULT,y=20*SPRITE_SIZE_MULT,
                                              group=clones.dudeg,batch=self.batch)
        else:
            self.cselect=pyglet.sprite.Sprite(clones.base_defenses[self.selected].imageR,
                                              x=100*SPRITE_SIZE_MULT,y=20*SPRITE_SIZE_MULT,
                                              group=clones.dudeg,batch=self.batch)
        self.cselect.scale=3
        self.cselect_cost.text=str(int(clones.base_defenses[self.selected].base_cost))
    def update_camx(self,x):
        self.camx+=x
        clones.camx=self.camx
        self.mapp.update(self.camx)
        for e in self.game.clones[1]+self.game.clones[0]:
            e.graphics_update()
        self.bg_red.vertices[0::2]=[e-x for e in self.bg_red.vertices[0::2]]
        self.bg_blue.vertices[0::2]=[e-x for e in self.bg_blue.vertices[0::2]]
    def key_press(self,symbol,modifiers):
        if symbol==key.ENTER:
            self.try_finish()
        elif symbol==key.A:
            if not (self.side==1 and self.camx==SCREEN_WIDTH//2):
                self.update_camx(-200)
        elif symbol==key.D:
            if not (self.side==0 and self.camx==-SCREEN_WIDTH//2):
                self.update_camx(200)
    def mouse_press(self,x,y,button,modifiers):
        c=self.selected
        if self.money>=clones.base_defenses[c].base_cost:
            connection.Send({"action":"place_thing","x":x//SPRITE_SIZE_MULT+self.camx,
                             "y":y//SPRITE_SIZE_MULT,"c":c})
    def try_finish(self):
        connection.Send({"action":"finish_base"})
    def place_thing(self,c,side,x,y):
        if side==self.side:
            self.money-=int(clones.base_defenses[c].base_cost)
            self.money_label.text=str(self.money)
        self.game.add_base_defense(c,side,x,y)
    def finish(self):
        self.bg_blue.delete()
        self.bg_red.delete()
        self.cselect.delete()
        self.cselect_cost.delete()
        self.money_label.delete()
        self.win.money_label.batch=self.batch
        self.win.main=mode_testing(self.win,self.batch,self.mapp,self.game)
        self.win.cc.start(self.side)

class windoo(pyglet.window.Window):
    def start(self):
        self.mainBatch = pyglet.graphics.Batch()
        self.money=self.sec=self.frames=0
        self.fpscount=pyglet.text.Label(x=5,y=5,text="aaa",color=(255,255,255,255),
                                        group=pyglet.graphics.OrderedGroup(4),batch=self.mainBatch)
        self.money_label=pyglet.text.Label(x=SCREEN_WIDTH-20,y=SCREEN_HEIGHT,text=str(int(self.money)),
                                           color=(255,255,0,255),group=pyglet.graphics.OrderedGroup(4),
                                           anchor_x="right",anchor_y="top",batch=self.mainBatch,
                                           font_size=int(40*SPRITE_SIZE_MULT))
        self.mouseheld=False
        self.cc=mode_choosing(self,self.mainBatch)
        self.bb=None
        self.main=None
        self.current_mode=mode(self,self.mainBatch)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
    def on_mouse_motion(self,x, y, dx, dy):
        self.current_mode.mouse_move(x,y,dx,dy)
    def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
        self.current_mode.mouse_drag(x,y,dx,dy,button,modifiers)
    def on_close(self):
        self.close()
        connection.Send({"action":"quit"})
        connection.Pump()
        connection.close()
        os._exit(0)
    def tick(self,dt):
        self.dispatch_events()
        self.check(dt)
        self.current_mode.tick(dt)
    def on_key_press(self,symbol,modifiers):
        self.current_mode.key_press(symbol,modifiers)
    def on_key_release(self,symbol,modifiers):
        self.current_mode.key_release(symbol,modifiers)
    def on_mouse_release(self, x, y, button, modifiers):
        self.mouseheld=False
        self.current_mode.mouse_release(x,y,button,modifiers)
    def on_resize(self,width,height):
        super().on_resize(width,height)
        self.current_mode.resize(width,height)
    def on_mouse_press(self,x,y,button,modifiers):
        self.mouseheld=True
        self.current_mode.mouse_press(x,y,button,modifiers)
    def on_mouse_scroll(self,x, y, scroll_x, scroll_y):
        self.current_mode.mouse_scroll(x, y, scroll_x, scroll_y)
    def on_deactivate(self):
        self.minimize()
    def check(self,dt):
        self.sec+=dt
        self.frames+=1
        self.money_label.text=str(int(self.money))
        if self.sec>1:
            self.sec-=1
            self.fpscount.text=str(self.frames)
            self.frames=0

place = windoo(caption='test',fullscreen=True)
place.start()
pyglet.clock.schedule_interval(place.tick,1.0/60)

while not nwl.start:
    connection.Pump()
    pyglet.clock.tick()
    nwl.Pump()
while True:
    try:
        connection.Pump()
        pyglet.clock.tick()
        nwl.Pump()
    except Exception as a:
        place.close()
        place.dispatch_events()
        raise(a)
