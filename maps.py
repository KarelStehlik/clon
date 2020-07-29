from imports import *
import images
map1=[]
class platform:
    graphicx=0
    def __init__(self,w,h,x,y):
        self.img=images.platform
        self.w=w
        self.h=h
        self.x=x
        self.y=y
    def batch(self,batch):
        self.pic=pyglet.sprite.Sprite(self.img,self.x,self.y,batch=batch)
        self.pic.scale_x=self.w/self.pic.width
        self.pic.scale_y=self.h/self.pic.height
    def draw(self):
        self.pic.x=self.graphicx
        self.pic.draw()
        
map1+=[platform(20000,20,-600,0),
       platform(200,30,500,100),
       platform(200,30,200,200)]
maps=[map1]
