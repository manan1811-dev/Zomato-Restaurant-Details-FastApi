from fastapi import FastAPI
from parser import *


app =FastAPI()

@app.post("/resturant/data/")
def featch(url : str):
    data = parser(url)
    if data:
        return {
            'message':'data featch successfully!',
            'response':data
        }
    else:
        return {
            'message':'error in api'
        }