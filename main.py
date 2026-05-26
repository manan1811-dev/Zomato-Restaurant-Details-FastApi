from request import *
from fastapi import FastAPI
from models import *
import re
from paser import *


# data=request("https://www.zomato.com/ahmedabad/la-pinoz-pizza-vatva/order")
# print(data)

app = FastAPI()

@app.post("/getdata")
def get_data(item: url):
    data= parser(item.url,0)
    return data

    
