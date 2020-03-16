import requests
import time
t0=time.time()
u1="http://127.0.0.1:5000/a_press"
u2="http://greycite.knowledgeblog.org/json?uri=http%3A%2F%2Fblog.dhimmel.com%2Firreproducible-timestamps%2F"
side=requests.get(u1)
print(str(side.text))
