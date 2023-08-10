from gps import *
import time
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 

try:
    while True:
        report = gpsd.next()
        if report['class'] == 'TPV':
            GPSlat = getattr(report, 'lat', 0.0)
            GPSlon = getattr(report, 'lon', 0.0)
            GPStime = getattr(report, 'time','')
            GPSalt = getattr(report, 'alt','nan')
            GPSepv = getattr(report, 'epv','nan')
            GPSept = getattr(report, 'ept','nan')
            GPSspeed = getattr(report, 'speed','nan')
            GPSclimb = getattr(report, 'climb','nan')

            print(f'''
            lat : {GPSlat}
            lon : {GPSlon}
            time : {GPStime}
            alt : {GPSalt}
            epv : {GPSepv}
            ept : {GPSept}
            speed : {GPSspeed}
            climb : {GPSclimb}  
            ''')
        time.sleep(1)

        
except KeyboardInterrupt:
    print("Keyboardinterrupt!!")
finally:
    print("exit")