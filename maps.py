from imports import *
import images
from constants import *
mappg=pyglet.graphics.OrderedGroup(1)
class platform:
    graphicx=0
    def __init__(self,dat):
        self.w=dat[0]
        self.h=dat[1]
        self.x=dat[2]
        self.y=dat[3]
        self.pic=0
    def create_image(self,batch):
        global mappg
        self.pic=pyglet.sprite.Sprite(images.platform,x=self.x*SPRITE_SIZE_MULT,
                                      y=self.y*SPRITE_SIZE_MULT,batch=batch,
                                      group=mappg)
        self.pic.scale_x=SPRITE_SIZE_MULT*self.w/images.platform.width
        self.pic.scale_y=SPRITE_SIZE_MULT*self.h/images.platform.height
    def batch(self,batch):
        a=platform([self.w,self.h,self.x,self.y])
        a.create_image(batch)
        return a
    def draw(self):
        self.pic.x=self.graphicx
        self.pic.draw()
a=open("test.txt","r")
x=a.read().split("/")
maps=[[platform([int(float(t)) for t in i.split(",")]) for i in e.split("\n")] for e in x]
