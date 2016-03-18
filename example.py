import json
import requests

data=json.dumps({'num':16072629999})
url='https://arrowapplication.herokuapp.com/'
r = requests.post(url, data=data,auth=('user', 'pass'))