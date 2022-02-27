'''
Created on Feb 10, 2012

@author: tufan
'''

import time
import pyproj

import log

dp_log = log.dp_log

class PlatformDataException(Exception):
    '''Base exeption class
    '''
    def __init__(self, s=None):
        self.msg = s
    
    def getMessage(self):
        if self.msg != None:
            return self.msg
        return "PlatformData Exception"
    
    
class Platform (object):
    
    def __init__ (self):
        self.updated = time.time()
        self.g = pyproj.Geod (ellps='WGS84')
        self.lati = None
        self.longi = None
        self.course = 0.0
        self.speed = 0.0

    def updatePos (self, lati, longi, datetime):
        ''' updates position to given parameters
        @TODO a huge change in position must be checked 
        '''
        if datetime < self.updated:
            # raise PlatformDataException ("Time error!") is possible if c&s data has been published before running the platform/data provider
            pass
                 
        self.lati = lati
        self.longi = longi
        self.updated = datetime
    
    def updateCrsSpd (self, course, speed, datetime):
        ''' advances platform position 
            first move platform upto datetime w/ previous course and speed values
            then move platform upto now with given course and speed  
        '''    
        if datetime < self.updated:
            dp_log.error("Course+Speed datetime is older then last position update!")
            # raise PlatformDataException ("Invalid time!") is possible if c&s data has been published before running the platform/data provider 
        
        ''' move platform to the position where crsspd update came
            with prevous course and speed values    
        '''  
        self._advanceToTime(datetime)

        "update course and / or speed"
        if course is not None: 
            self.course = course
        if speed is not None:
            self.speed = speed
                
        ''' and re-advance platform postion to the current time
        '''
        self.advance()
        
       
    def advance (self):
        ''' advances position to now with latest course and speed values
        '''
        now = time.time()
        if now < self.updated:
            dp_log.error("Platform update time is newer! Check clocks of the system!")
            raise PlatformDataException("Invalid time!")
        
        if self._advanceToTime(now) :
            return {'latitude':self.lati,
                    'longitude':self.longi,
                    'course':self.course,
                    'speed':self.speed,
                    'timeval':self.updated}
        return None
                    
    def dump (self):
        if self.lati is not None:
            print('lat:' + str(self.lati)),
        if self.longi is not None:    
            print('long:' + str(self.longi)),
        if self.course is not None:
            print('crs:' + str(self.course)),
        if self.speed is not None: 
            print('spd:' + str(self.speed)),
        print(self.updated)
        
        
    def _advanceToTime(self, datetime):
        
        if self.lati is None:
            dp_log.warn("Position has not been set cannot advance platform!")
            return False
        
        distance = (datetime - self.updated) * self.speed
        
        new_long, new_lat, _ = self.g.fwd(self.longi, self.lati, self.course, distance)

        self.lati = new_lat
        self.longi = new_long
        self.updated = datetime
        
        return True

    
