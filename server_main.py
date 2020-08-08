from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time
cn=False
class player_channel(Channel):
    def Network(self, data):
        pass
    def Network_myaction(self, data):
        cn.Send({"action": "myaction", "a": data["a"]*2})

class cw_server(Server):
    channelClass = player_channel
    def Connected(self, channel, addr):
        global cn
        cn+=[channel]
cw_server()
srvr=cw_server()
print(srvr.addr)
while True:
    srvr.Pump()
    if cn:
        cn.Pump()
    time.sleep(0.0001)
