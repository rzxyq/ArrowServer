import json
import requests

data=json.dumps({'num':16073797896})
url='https://arrowapplication.herokuapp.com/phoneAuth/'
url2='http://localhost:8000/phoneAuth/'

r = requests.post(url, data=data,auth=('user', 'pass'))