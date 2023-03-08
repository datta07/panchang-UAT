from panchang_nondatabase import Panchang
from fastapi import FastAPI
import time

app=FastAPI()

#http://127.0.0.1:8000/panchang?date=28-07-2000&alt=0&lng=16.015066&lat=80.825353
#uvicorn main:app --host 0.0.0.0 --port 10000
@app.get("/panchang")
def panchang(date=time.strftime("%d-%m-%Y"),lat="75.7764300",lng="23.1823900",alt="0.494"):
	date=date.split("-")
	return Panchang(int(date[0]),int(date[1]),int(date[2]),lng,lat,alt).data
