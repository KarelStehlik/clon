import pyglet
gunmanR=pyglet.resource.image("imagefolder/BGunman.png")
gunmanG=pyglet.resource.image("imagefolder/GGunman.png")
mixerR=pyglet.resource.image("imagefolder/BMixer.png")
mixerG=pyglet.resource.image("imagefolder/GMixer.png")
gunmanG.width=40
gunmanG.height=70
gunmanR.width=40
gunmanR.height=70
mixerG.width=35
mixerG.height=60
mixerR.width=35
mixerR.height=60
for e in [gunmanG,gunmanR,mixerG,mixerR]:
    e.anchor_x=e.width//2
gunmanG.anchor_x-=5
gunmanR.anchor_x-=5

bullet=pyglet.resource.image("imagefolder/Bullet.png")
bullet.width=bullet.height=6
bullet.anchor_x=bullet.anchor_y=3

BazookaBullet=pyglet.resource.image("imagefolder/BazookaBullet.png")
BazookaBullet.anchor_x=BazookaBullet.width
BazookaBullet.anchor_y=BazookaBullet.height//2

buttonG=pyglet.image.load("imagefolder/GreenButton.png")
buttonR=pyglet.image.load("imagefolder/RedButton.png")
platform=pyglet.image.load("imagefolder/platform.png")
cloneFrame=pyglet.image.load("imagefolder/clone_select.png")