from imports import *
import images
from constants import *
mappg=pyglet.graphics.OrderedGroup(1)
class platform:
    graphicx=0
    def __init__(self,w,h,x,y):
        self.w=w
        self.h=h
        self.x=x
        self.y=y
        self.pic=0
    def create_image(self,batch):
        global mappg
        self.pic=pyglet.sprite.Sprite(images.platform,x=self.x*SPRITE_SIZE_MULT,
                                      y=self.y*SPRITE_SIZE_MULT,batch=batch,
                                      group=mappg)
        self.pic.scale_x=SPRITE_SIZE_MULT*self.w/images.platform.width
        self.pic.scale_y=SPRITE_SIZE_MULT*self.h/images.platform.height
    def batch(self,batch):
        a=platform(self.w,self.h,self.x,self.y)
        a.create_image(batch)
        return a
    def draw(self):
        self.pic.x=self.graphicx
        self.pic.draw()
        
map1=[platform(20000,20,-10000,0),
       platform(200,30,500,100),
       platform(200,30,200,200),
      platform(20,600,100,20),
      platform(20,500,100,20),
      platform(20,400,100,20),
      platform(20,300,100,20),
      platform(20,200,100,20),
      platform(20,100,100,20),
      platform(200,30,1000,100)]
map2=[platform(20000,20,-10000,0),
       platform(200,30,500,100),
       platform(200,30,200,200),
       platform(200,30,500,300),
       platform(200,30,200,400),
      platform(200,30,1000,100)]
maps=[map1,map2]
