import pyglet
gunmanR=pyglet.resource.image("imagefolder/BGunman.png")
gunmanG=pyglet.resource.image("imagefolder/GGunman.png")
mixerR=pyglet.resource.image("imagefolder/BMixer.png")
mixerG=pyglet.resource.image("imagefolder/GMixer.png")
teleG=pyglet.resource.image("imagefolder/GTele.png")
teleR=pyglet.resource.image("imagefolder/BTele.png")
ZookaG=pyglet.resource.image("imagefolder/GZooka.png")
ZookaR=pyglet.resource.image("imagefolder/BZooka.png")
gunmanG.width=40
gunmanG.height=70
gunmanR.width=40
gunmanR.height=70
mixerG.width=35
mixerG.height=60
mixerR.width=35
mixerR.height=60
teleG.width=50
teleG.height=80
teleR.width=50
teleR.height=80
ZookaG.anchor_x=55
ZookaG.width=200
ZookaG.height=68
ZookaR.anchor_x=55
ZookaR.width=200
ZookaR.height=68
for e in [gunmanG,gunmanR,mixerG,mixerR,teleG,teleR]:
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
