from datetime import date, datetime, timezone, timedelta
import astral, astral.sun, astral.moon
import pytz
import time

def seconds_to_hrs(seconds):
	if seconds is not None:
		seconds = int(seconds)
		d = seconds // (3600 * 24)
		h = seconds // 3600 % 24
		m = seconds % 3600 // 60
		s = seconds % 3600 % 60
		if d > 0:
			return '{:02d}days {:02d}hrs {:02d}mins {:02d}secs'.format(d, h, m, s)
		elif h > 0:
			return '{:02d}hrs {:02d}mins {:02d}secs'.format(h, m, s)
		elif m > 0:
			return '{:02d}mins {:02d}secs'.format(m, s)
		elif s > 0:
			return '{:02d}secs'.format(s)
	return '-'

class Panchang:
	def __init__(self,dat,month,year, lat,lon,alt,tz='Asia/Kolkata'):
		self.latitude = lat
		self.longitude = lon
		self.altitude = alt
		self.tz = pytz.timezone(tz)
		self.tz_name = tz
		self.for_date = date(year, month, dat)
		self.data={}

		self.performOperations()

	def performOperations(self):
		self.calSun()
		self.calMoon()
		self.data["weekday"]=(self.for_date.weekday()+1)%7
		self.bramhaMuhrat()
		self.abhijit()
		self.godhuli()
		self.pratahSandhya()
		self.vijayMuhurat()
		self.sayahnaSandhya()
		self.nishitaMuhurta()
		self.rahuKal()
		self.gulikaiKal()
		self.yamaganda()
		self.durMuhurtam()

	def calSun(self):
		l = astral.LocationInfo('Custom Name', 'My Region', self.tz_name, self.latitude, self.longitude)
		s = astral.sun.sun(l.observer, date=self.for_date)
		self.data["sunrise"]={"time":str(s['sunrise'].astimezone(self.tz)),"timestamp":s['sunrise'].timestamp()}
		self.data["sunset"]={"time":str(s['sunset'].astimezone(self.tz)),"timestamp":s['sunset'].timestamp()}

		s1 = astral.sun.sun(l.observer, date=self.for_date+timedelta(days=1))
		self.data["next_sunrise"]={"time":str(s1['sunrise'].astimezone(self.tz)),"timestamp":s1['sunrise'].timestamp()}
		s2 = astral.sun.sun(l.observer, date=self.for_date+timedelta(days=-1))
		self.data["prev_sunset"]={"time":str(s2['sunset'].astimezone(self.tz)),"timestamp":s2['sunset'].timestamp()}

		self.data["dinamana"]=seconds_to_hrs(self.data["sunset"]["timestamp"]-self.data["sunrise"]["timestamp"])
		self.data["ratrimana"]=seconds_to_hrs(s1['sunrise'].timestamp()-self.data["sunset"]["timestamp"])
		rt1=(self.data["sunrise"]["timestamp"]+self.data["sunset"]["timestamp"])/2
		self.data["madhyahna"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}

	def calMoon(self):
		l = astral.LocationInfo('Custom Name', 'My Region', self.tz_name, self.latitude, self.longitude)
		
		try:
			s = astral.moon.moonrise(l.observer, date=self.for_date)
			self.data["moonrise"]={"time":str(s.astimezone(self.tz)),"timestamp":s.timestamp()}
		except Exception:
			try:
				s = astral.moon.moonrise(l.observer, date=self.for_date+timedelta(days=1))
				self.data["moonrise"]={"time":str(s.astimezone(self.tz)),"timestamp":s.timestamp()}
			except Exception:
				self.data["moonset"]=None
		try:
			s = astral.moon.moonset(l.observer, date=self.for_date)
		except Exception:
			try:
				s = astral.moon.moonset(l.observer, date=self.for_date+timedelta(days=1))
			except Exception:
				self.data["moonset"]=None
				return		
		self.data["moonset"]={"time":str(s.astimezone(self.tz)),"timestamp":s.timestamp()}

	def bramhaMuhrat(self):
		t1=self.data["prev_sunset"]["timestamp"]
		t2=self.data["sunrise"]["timestamp"]

		part=13
		rt1=t1+(t2-t1)/15*part
		rt2=t1+(t2-t1)/15*(part+1)
		self.data["bramhaMuhrat"]={}
		self.data["bramhaMuhrat"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["bramhaMuhrat"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}

	def abhijit(self):
		if self.data["weekday"]==3:
			self.data["abhijit"]=None
			return None

		t1=self.data["sunrise"]["timestamp"]
		t2=self.data["sunset"]["timestamp"]

		part=7
		rt1=t1+(t2-t1)/15*part
		rt2=t1+(t2-t1)/15*(part+1)
		self.data["abhijit"]={}
		self.data["abhijit"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["abhijit"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}

	def godhuli(self):
		t1=self.data["sunset"]["timestamp"]
		t2=self.data["next_sunrise"]["timestamp"]

		part=0
		rt1=t1+(t2-t1)/15*part
		rt2=t1+(t2-t1)/15*(part+1)
		rt2-=((t2-t1)/30)
		self.data["godhuli"]={}
		self.data["godhuli"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["godhuli"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}
	
	def pratahSandhya(self):
		t1=self.data["sunset"]["timestamp"]
		t2=self.data["next_sunrise"]["timestamp"]

		part=14
		rt1=t1+(t2-t1)/15*part
		rt1-=((t2-t1)/30)
		rt2=t1+(t2-t1)/15*(part+1)
		
		self.data["pratahSandhya"]={}
		self.data["pratahSandhya"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["pratahSandhya"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}

	def vijayMuhurat(self):
		t1=self.data["sunrise"]["timestamp"]
		t2=self.data["sunset"]["timestamp"]

		part=5
		rt1=t1+(t2-t1)/8*part
		rt1+=((t2-t1)/24)
		rt2=t1+(t2-t1)/8*(part+1)
		rt2-=((t2-t1)/64)
				
		self.data["vijayMuhurat"]={}
		self.data["vijayMuhurat"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["vijayMuhurat"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}

	def sayahnaSandhya(self):
		t1=self.data["sunset"]["timestamp"]
		t2=self.data["next_sunrise"]["timestamp"]

		part=0
		rt1=t1+(t2-t1)/15*part
		rt2=t1+(t2-t1)/15*(part+1)
		rt2+=((t2-t1)/30)		

		self.data["sayahnaSandhya"]={}
		self.data["sayahnaSandhya"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["sayahnaSandhya"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}

	def nishitaMuhurta(self):
		t1=self.data["sunset"]["timestamp"]
		t2=self.data["next_sunrise"]["timestamp"]

		part=7
		rt1=t1+(t2-t1)/15*part
		rt2=t1+(t2-t1)/15*(part+1)	

		self.data["nishitaMuhurta"]={}
		self.data["nishitaMuhurta"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["nishitaMuhurta"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}

	def rahuKal(self):
		t1=self.data["sunrise"]["timestamp"]
		t2=self.data["sunset"]["timestamp"]

		parts=[8,2,7,5,6,4,3]
		part=parts[self.data["weekday"]]-1
		rt1=t1+(t2-t1)/8*part
		rt2=t1+(t2-t1)/8*(part+1)	

		self.data["rahuKal"]={}
		self.data["rahuKal"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["rahuKal"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}

	def gulikaiKal(self):
		t1=self.data["sunrise"]["timestamp"]
		t2=self.data["sunset"]["timestamp"]

		parts=[7,6,5,4,3,2,1]
		part=parts[self.data["weekday"]]-1
		rt1=t1+(t2-t1)/8*part
		rt2=t1+(t2-t1)/8*(part+1)	

		self.data["gulikaiKal"]={}
		self.data["gulikaiKal"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["gulikaiKal"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}

	def yamaganda(self):
		t1=self.data["sunrise"]["timestamp"]
		t2=self.data["sunset"]["timestamp"]

		parts=[5,4,3,2,1,7,6]
		part=parts[self.data["weekday"]]-1
		rt1=t1+(t2-t1)/8*part
		rt2=t1+(t2-t1)/8*(part+1)	

		self.data["yamaganda"]={}
		self.data["yamaganda"]["start"]={"time":datetime.fromtimestamp(rt1).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt1}
		self.data["yamaganda"]["end"]={"time":datetime.fromtimestamp(rt2).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":rt2}

	def durMuhurtam(self):
		t1=self.data["sunrise"]["timestamp"]
		t2=self.data["sunset"]["timestamp"]

		self.data["durMuhurtam"]=[]

		hrs=[]
		if self.data["weekday"]==6:
			part=0
			rt1=t1+(t2-t1)/15*part
			rt2=t1+(t2-t1)/15*(part+2)
			hrs.append((rt1,rt2))
		elif self.data["weekday"]==2:
			part=3
			rt1=t1+(t2-t1)/15*part
			rt2=t1+(t2-t1)/15*(part+1)
			hrs.append((rt1,rt2))
			t1=t2
			t2=self.data["next_sunrise"]["timestamp"]
			part=6
			rt1=t1+(t2-t1)/15*part
			rt2=t1+(t2-t1)/15*(part+1)
			hrs.append((rt1,rt2))
		else:
			parts=[[13],[8,11],[3,7],[7],[5,11],[3,8]]
			part=parts[self.data["weekday"]]
			for i in part:
				rt1=t1+(t2-t1)/15*i
				rt2=t1+(t2-t1)/15*(i+1)
				hrs.append((rt1,rt2))
		
		for i in hrs:
			self.data["durMuhurtam"].append({
				"start":{"time":datetime.fromtimestamp(i[0]).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":i[0]},
				"end":{"time":datetime.fromtimestamp(i[1]).astimezone(self.tz).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":i[1]}
				})

'''pan=Panchang(17,7,2023,13.6833300,79.3500000,0.858,'Asia/Kolkata')
print(pan.data)'''