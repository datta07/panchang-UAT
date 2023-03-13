from datetime import date, datetime, timezone, timedelta
import pytz
import swisseph as swe
from math import ceil


def unwrap_angles(angles):
  result = angles
  for i in range(1, len(angles)):
    if result[i] < result[i-1]: result[i] += 360
  return result

def inverse_lagrange(x, y, ya):
  total = 0
  for i in range(len(x)):
    numer = 1
    denom = 1
    for j in range(len(x)):
      if j != i:
        numer *= (ya - y[j])
        denom *= (y[i] - y[j])
    total += numer * x[i] / denom
  return total

def sunrise(jd,loc):
    #result = swe.rise_trans(jd, swe.SUN, loc[0], loc[1],alt=loc[2], rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
    result = swe.rise_trans(jd , swe.SUN, swe.CALC_RISE | swe.BIT_HINDU_RISING, loc ,1013.25, 15, swe.FLG_SWIEPH)
    rise = result[1][0]
    return rise
    tm=swe.revjul(rise)
    dt1=datetime.datetime.strptime(str(2023)+' '+str(3)+' '+str(12), '%Y %m %d')+timedelta(hours=tm[-1])
    return [rise,dt1.astimezone(pytz.timezone("Asia/Kolkata")).strftime('%d/%m/%Y %I:%M:%S %p')]

def moon_phase(jd):
    solar_long = swe.calc_ut(jd, swe.SUN, flags = swe.FLG_SWIEPH)[0]
    lunar_long = swe.calc_ut(jd, swe.MOON, flags = swe.FLG_SWIEPH)[0]
    moon_phase = (lunar_long[0] - solar_long[0]) % 360
    return moon_phase
  
def to_timestamp(jd):
    rev_jd=swe.revjul(jd,swe.GREG_CAL)
    return (datetime(year=rev_jd[0],month=rev_jd[1],day=rev_jd[2])+timedelta(hours=rev_jd[3])).timestamp()

def tithi_paksha(sunrise_jd,today_jd):
    ans=[]
    tithis = [['Śukla pakṣa', 'prathamā'], ['Śukla pakṣa', 'dvitīyā'], ['Śukla pakṣa', 'tṛtīyā'], ['Śukla pakṣa', 'caturthī'], ['Śukla pakṣa', 'pañcamī'], ['Śukla pakṣa', 'ṣaṣṭhī'], ['Śukla pakṣa', 'saptamī'], ['Śukla pakṣa', 'aṣṭhamī'], ['Śukla pakṣa', 'navamī'], ['Śukla pakṣa', 'daśamī'], ['Śukla pakṣa', 'ekādaśī'], ['Śukla pakṣa', 'dvādaśī'], ['Śukla pakṣa', 'trayodaśī'], ['Śukla pakṣa', 'caturdasī'], ['no paksa', 'Pūrṇimā'], ['Kṛṣṇa pakṣa', 'prathamā'], ['Kṛṣṇa pakṣa', 'dvitīyā'], ['Kṛṣṇa pakṣa', 'tṛtīyā'], ['Kṛṣṇa pakṣa', 'caturthī'], ['Kṛṣṇa pakṣa', 'pañcamī'], ['Kṛṣṇa pakṣa', 'ṣaṣṭhi'], ['Kṛṣṇa pakṣa', 'saptamī'], ['Kṛṣṇa pakṣa', 'aṣṭhamī'], ['Kṛṣṇa pakṣa', 'navamī'], ['Kṛṣṇa pakṣa', 'daśamī'], ['Kṛṣṇa pakṣa', 'ekādaśī'], ['Kṛṣṇa pakṣa', 'dvādaśī'], ['Kṛṣṇa pakṣa', 'trayodaśī'], ['Kṛṣṇa pakṣa', 'caturdasī'], ['no paksa', 'Amāvāsyā']]
    moonphase=moon_phase(sunrise_jd)
    today=ceil(moonphase / 12)
    degreesleft=ceil(moonphase / 12)*12-moonphase

    offsets = [0.25, 0.5, 0.75, 1.0]  
    lunar_long_diff = [ (swe.calc_ut(sunrise_jd + t, swe.MOON, flags = swe.FLG_SWIEPH)[0][0] - swe.calc_ut(sunrise_jd, swe.MOON, flags = swe.FLG_SWIEPH)[0][0]) % 360 for t in offsets ]
    solar_long_diff = [ (swe.calc_ut(sunrise_jd + t, swe.SUN, flags = swe.FLG_SWIEPH)[0][0] - swe.calc_ut(sunrise_jd, swe.SUN, flags = swe.FLG_SWIEPH)[0][0])  % 360 for t in offsets ]
    relative_motion = [ moon - sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff) ]

    approx_end = inverse_lagrange(offsets, relative_motion, degreesleft)
    ends = (sunrise_jd + approx_end -today_jd)
    ans.append([tithis[today-1][1]+" : "+tithis[today-1][0],to_timestamp(today_jd+ends)])

    moon_phase_tmrw = moon_phase(sunrise_jd + 1)
    tomorrow = ceil(moon_phase_tmrw / 12)

    isSkipped = (tomorrow - today) % 30 > 1
    if isSkipped:
      degrees_left = (today + 1)*12 - moonphase
      approx_end = inverse_lagrange( offsets,relative_motion, degrees_left)
      ends = (sunrise_jd + approx_end -today_jd)
      ans.append([tithis[today][1]+" : "+tithis[today][0],to_timestamp(today_jd+ends)])

    return ans

def nakshatra(sunrise_jd,today_jd):
    ans=[]
    nakshatras=['Aśvinī', 'Bharaṇī', 'Kṛttikā', 'Rohiṇī', 'Mṛgaśīrā', 'Ārdrā', 'Punarvasū', 'Puṣya', 'Āśleṣā', 'Maghā', 'Pūrvaphalgunī', 'Uttaraphalgunī', 'Hasta', 'Cittā', 'Svāti', 'Viśākhā', 'Anūrādhā', 'Jyeṣṭhā', 'Mūlā', 'Pūrvāṣāḍhā', 'Uttarāṣāḍhā', 'Śravaṇā', 'Dhaniṣṭhā', 'Śatabhiṣā', 'Pūrvābhādrā', 'Uttarābhādrā', 'Revatī']
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [ (swe.calc_ut(sunrise_jd + t, swe.MOON, flags = swe.FLG_SWIEPH)[0][0] - swe.get_ayanamsa_ut(sunrise_jd)) % 360 for t in offsets]

    nak = ceil(longitudes[0] * 27 / 360)
    
    y = unwrap_angles(longitudes)
    approx_end = inverse_lagrange(offsets, y, nak * 360 / 27)
    ends = (sunrise_jd - today_jd + approx_end) 
    ans.append([nakshatras[nak-1],to_timestamp(today_jd+ends)])
    
    nak_tmrw = ceil(longitudes[-1] * 27 / 360)
    isSkipped = (nak_tmrw - nak) % 27 > 1
    if isSkipped:
      nak+=1
      approx_end = inverse_lagrange(offsets, longitudes, nak * 360 / 27)
      ends = (sunrise_jd - today_jd + approx_end) * 24 
      ans.append([nakshatras[nak-1],to_timestamp(today_jd+ends)])
    
    return ans

def yoga(sunrise_jd,today_jd):
    ans=[]
    yogas=['Viṣkumbha', 'Prīti', 'Āyuṣmān', 'Saubhāgya', 'Śobhana', 'Atigaṇḍa', 'Sukarmā', 'Dhṛti', 'Śūla', 'Gaṇḍa', 'Vṛddhi', 'Dhruva', 'Vyāghāta', 'Harṣaṇa', 'Vajra', 'Siddhi', 'Vyatīpāta', 'Vārīyana', 'Parigha', 'Śiva', 'Siddha', 'Sādhya', 'Śubha', 'Śukla', 'Brahma', 'Aindra', 'Vaidhṛti']
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    lunar_long = (swe.calc_ut(sunrise_jd , swe.MOON, flags = swe.FLG_SWIEPH)[0][0] - swe.get_ayanamsa_ut(sunrise_jd)) % 360
    solar_long = (swe.calc_ut(sunrise_jd, swe.SUN, flags = swe.FLG_SWIEPH)[0][0] - swe.get_ayanamsa_ut(sunrise_jd)) % 360
    total = (lunar_long + solar_long) % 360

    yog = ceil(total * 27 / 360)
    degrees_left = yog * (360 / 27) - total

    offsets = [0.25, 0.5, 0.75, 1.0]
    lunar_long_diff = [ (swe.calc_ut(sunrise_jd+t , swe.MOON, flags = swe.FLG_SWIEPH)[0][0] - swe.calc_ut(sunrise_jd , swe.MOON, flags = swe.FLG_SWIEPH)[0][0]) % 360 for t in offsets ]
    solar_long_diff = [ (swe.calc_ut(sunrise_jd+t , swe.SUN, flags = swe.FLG_SWIEPH)[0][0] - swe.calc_ut(sunrise_jd , swe.SUN, flags = swe.FLG_SWIEPH)[0][0]) % 360 for t in offsets ]

    total_motion = [moon + sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff)]
    
    approx_end = inverse_lagrange(offsets, total_motion, degrees_left)
    ends = (sunrise_jd + approx_end - today_jd)
    ans.append([yogas[yog-1],to_timestamp(today_jd+ends)])

    lunar_long_tmrw = (swe.calc_ut(sunrise_jd+1 , swe.MOON, flags = swe.FLG_SWIEPH)[0][0] - swe.get_ayanamsa_ut(sunrise_jd + 1)) % 360
    solar_long_tmrw = (swe.calc_ut(sunrise_jd+1 , swe.SUN, flags = swe.FLG_SWIEPH)[0][0] - swe.get_ayanamsa_ut(sunrise_jd + 1)) % 360

    total_tmrw = (lunar_long_tmrw + solar_long_tmrw) % 360
    tomorrow = ceil(total_tmrw * 27 / 360)
    isSkipped = (tomorrow - yog) % 27 > 1
    if isSkipped:
      yog+=1
      degrees_left = yog * (360 / 27) - total
      approx_end = inverse_lagrange(offsets, total_motion, degrees_left)
      ends = (sunrise_jd + approx_end - today_jd) * 24
      ans.append([yogas[yog-1],to_timestamp(today_jd+ends)])
    return ans
    
def karana(sunrise_jd,today_jd):
    ans=[]
    karanas=['Kiṃstughna', 'Bava', 'Bālava', 'Kaulava', 'Taitila', 'Garaja', 'Vaṇija', 'Viṣṭi', 'Bava', 'Bālava', 'Kaulava', 'Taitila', 'Garaja', 'Vaṇija', 'Viṣṭi', 'Bava', 'Bālava', 'Kaulava', 'Taitila', 'Garaja', 'Vaṇija', 'Viṣṭi', 'Bava', 'Bālava', 'Kaulava', 'Taitila', 'Garaja', 'Vaṇija', 'Viṣṭi', 'Bava', 'Bālava', 'Kaulava', 'Taitila', 'Garaja', 'Vaṇija', 'Viṣṭi', 'Bava', 'Bālava', 'Kaulava', 'Taitila', 'Garaja', 'Vaṇija', 'Viṣṭi', 'Bava', 'Bālava', 'Kaulava', 'Taitila', 'Garaja', 'Vaṇija', 'Viṣṭi', 'Bava', 'Bālava', 'Kaulava', 'Taitila', 'Garaja', 'Vaṇija', 'Viṣṭi', 'Śakuni', 'Catuṣpāda', 'Nāgava']
    
    moonphase = moon_phase(sunrise_jd)#(lunar_long - solar_long) % 360
    today = ceil(moonphase / 6)
    degreesleft = today * 6 - moonphase

    offsets = [0.25, 0.5, 0.75, 1.0]  
    lunar_long_diff = [ (swe.calc_ut(sunrise_jd + t, swe.MOON, flags = swe.FLG_SWIEPH)[0][0] - swe.calc_ut(sunrise_jd, swe.MOON, flags = swe.FLG_SWIEPH)[0][0]) % 360 for t in offsets ]
    solar_long_diff = [ (swe.calc_ut(sunrise_jd + t, swe.SUN, flags = swe.FLG_SWIEPH)[0][0] - swe.calc_ut(sunrise_jd, swe.SUN, flags = swe.FLG_SWIEPH)[0][0])  % 360 for t in offsets ]
    relative_motion = [ moon - sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff) ]
    
    approx_end = inverse_lagrange(offsets, relative_motion, degreesleft)
    ends = (sunrise_jd + approx_end -today_jd)
    ans.append([karanas[today-1],to_timestamp(today_jd+ends)])

    answer = int(today)
    moon_phase_tmrw = moon_phase(sunrise_jd + 1)
    tomorrow = ceil(moon_phase_tmrw / 6)

    isSkipped = (tomorrow - today) % 60 > 1
    while isSkipped:
      today+=1
      degrees_left = (today)*6 - moonphase
      approx_end = inverse_lagrange( offsets,relative_motion, degrees_left)
      ends = (sunrise_jd + approx_end -today_jd) 
      ans.append([karanas[today-1],to_timestamp(today_jd+ends)])

      answer = int(today)
      moon_phase_tmrw = moon_phase(sunrise_jd + 1)
      tomorrow = ceil(moon_phase_tmrw / 6)
      isSkipped = (tomorrow - today) % 60 > 1

    return ans            

def suryanakshatra(sunrise_jd,today_jd):
    ans=[]
    nakshatras=['Aśvinī', 'Bharaṇī', 'Kṛttikā', 'Rohiṇī', 'Mṛgaśīrā', 'Ārdrā', 'Punarvasū', 'Puṣya', 'Āśleṣā', 'Maghā', 'Pūrvaphalgunī', 'Uttaraphalgunī', 'Hasta', 'Cittā', 'Svāti', 'Viśākhā', 'Anūrādhā', 'Jyeṣṭhā', 'Mūlā', 'Pūrvāṣāḍhā', 'Uttarāṣāḍhā', 'Śravaṇā', 'Dhaniṣṭhā', 'Śatabhiṣā', 'Pūrvābhādrā', 'Uttarābhādrā', 'Revatī']
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [ (swe.calc_ut(sunrise_jd + t, swe.SUN, flags = swe.FLG_SWIEPH)[0][0] - swe.get_ayanamsa_ut(sunrise_jd)) % 360 for t in offsets]

    nak = ceil(longitudes[0] * 27 / 360)
    
    y = unwrap_angles(longitudes)
    approx_end = inverse_lagrange(offsets, y, nak * 360 / 27)
    ends = (sunrise_jd - today_jd + approx_end) 
    ans.append([nakshatras[nak-1],to_timestamp(today_jd+ends)])
    
    nak_tmrw = ceil(longitudes[-1] * 27 / 360)
    isSkipped = (nak_tmrw - nak) % 27 > 1
    if isSkipped:
      nak+=1
      approx_end = inverse_lagrange(offsets, longitudes, nak * 360 / 27)
      ends = (sunrise_jd - today_jd + approx_end) * 24 
      ans.append([nakshatras[nak-1],to_timestamp(today_jd+ends)])
    
    return ans



def summerize(arr,tdy,tmr):
  temp={}
  for i in arr:
    temp[i[0]]=i[1]
  arr=[]
  for i in temp:
    arr.append([i,temp[i]])
  
  ans={}
  if len(arr)==1:
    ans[arr[0][0]]={"start":None,"end":{"time":datetime.datetime.fromtimestamp(arr[0][1]).astimezone(pytz.timezone('Asia/Kolkata')).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":arr[0][1]}}
  else:
    for no in range(1,len(arr)):
      if (arr[no][1]>tdy) and (arr[no-1][1]>tmr):
        continue
      elif (arr[no][1]<tdy):
        continue
      ans[arr[no][0]]={"start":{"time":datetime.fromtimestamp(arr[no-1][1]).astimezone(pytz.timezone('Asia/Kolkata')).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":arr[no-1][1]},
                        "end":{"time":datetime.fromtimestamp(arr[no][1]).astimezone(pytz.timezone('Asia/Kolkata')).strftime('%d/%m/%Y %I:%M:%S %p'),"timestamp":arr[no][1]}}

  return ans

def summerize2(arr):
    return arr[0][0]
