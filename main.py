from panchang_nondatabase import Panchang
from fastapi import FastAPI
import time

app=FastAPI()

#http://127.0.0.1:8000/panchang?date=28-07-2000&alt=0&lng=80.825353&lat=16.015066
#uvicorn main:app --host 0.0.0.0 --port 10000
@app.get("/panchang")
def panchang(date=time.strftime("%d-%m-%Y"),lat="23.1823900",lng="75.7764300",alt="0.494",tz='Asia/Kolkata'):
	date=date.split("-")
	return Panchang(int(date[0]),int(date[1]),int(date[2]),lat,lng,alt,tz).data
