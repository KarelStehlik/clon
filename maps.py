from imports import *
import images
from constants import *
mappg=pyglet.graphics.OrderedGroup(0)
class platform:
    graphicx=0
    def __init__(self,w,h,x,y):
        self.img=images.platform
        self.w=w
        self.h=h
        self.x=x
        self.y=y
    def batch(self,batch):
        self.pic=pyglet.sprite.Sprite(self.img,self.x*SPRITE_SIZE_MULT,
                                      self.y*SPRITE_SIZE_MULT,batch=batch,
                                      group=mappg)
        self.pic.scale_x=self.w/self.img.width
        self.pic.scale_y=self.h/self.img.height
        self.pic.scale=SPRITE_SIZE_MULT
    def draw(self):
        self.pic.x=self.graphicx
        self.pic.draw()
        
map1=[platform(20000,20,-600,0),
       platform(200,30,500,100),
       platform(200,30,200,200),
      platform(20,600,100,20),
      platform(20,500,100,20),
      platform(20,400,100,20),
      platform(20,300,100,20),
      platform(20,200,100,20),
      platform(20,100,100,20),]
map2=[platform(20000,20,-600,0),
       platform(200,30,500,100),
       platform(200,30,200,200),
       platform(200,30,500,300),
       platform(200,30,200,400)]
maps=[map1,map2]
