#!/usr/bin/env python3

'''
Created on January 2012
@author: tufan
@description: DeadRecon the platform wrt position, course and speed provided
              For geographic/navigation calculations PROJ.4 software
             (now a part of The Open Source Geospatial Foundation) Python 
             module is used
@pub: /<hostname>/platform/data
@sub: /+/+/prop/data 
@pubsub:
'''

__version__ = "$Id$"

import os
import sys
import time
import platform
import argparse
import getpass
from io import StringIO
import json
import paho.mqtt.client as mqtt

import log
import dp_platform 

# -- module globals

dp_log = log.dp_log
dp_Platform = dp_platform.Platform() 

def on_connect(client, userdata, flgs, rc):
    if rc == 0:
        dp_log.debug ("Connected successfully with result code " + str(rc))
    else:
        dp_log.error ("Broker error! Cannot connect!")
        raise SystemExit
    
def on_publish(clinet, user_data, mid):
    dp_log.debug ("Published successfully!")


def on_subscribe(client, userdata, mid, granted_qos):
    dp_log.debug("Subscribed to " + str(mid) + " successfully.")


def on_message(client, userdata, msg):
    dp_log.debug("got message " + msg.topic + ":" + str(msg.payload))
   
    data = json.loads(msg.payload)
     
    print (data)
    if "/pos/prop/data" in msg.topic:
        print ("Position")
        dp_Platform.updatePos(data['latitude'], data['longitude'], data['datetime']) 
        
    if "/crsspd/prop/data" in msg.topic:
        print ("CourseSpeed")
        try:
            data['course']
        except KeyError:
            data['course'] = None
        try:
            data['speed']
        except KeyError:
            data['speed'] = None
        dp_Platform.updateCrsSpd(data['course'], data['speed'], data['datetime'])
    

def on_disconnect(clinet, user_data, rc):
    dp_log.debug("Disconnected successfully.")

def main():
    parser = argparse.ArgumentParser (prog="cl_propPosUpdate", description="Publishes given position data")
    parser.add_argument ("-t", "--host", dest="host", action="store", default="localhost", help="MQTT broker hostname")
    parser.add_argument ("-p", "--port", dest="port", action="store", default="1883", help="MQTT broker port")
 
    args = parser.parse_args()

    dp_log.debug (args.host + ', ' + args.port)

    cname = os.path.basename(sys.argv[0])
    hostname = platform.node().split('.')[0]
    username = getpass.getuser()

    mqtt_client = mqtt.Client(username + '@' + hostname + ':' + cname)
    
    mqtt_client.on_connect = on_connect 
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message

    result = mqtt_client.connect(host=args.host, port=int(args.port), keepalive=10) 

    if (result != 0):
        dp_log.error ("Error connecting to mqtt broker!")
        raise SystemExit

    (result, _) = mqtt_client.subscribe("/+/+/prop/data", 1)

    tpub = 0.0
    while (True):
        mqtt_client.loop()
        tnow = time.time()
        if (tnow - tpub) > 1.0: # update platform data no sooner then every second
            data = dp_Platform.advance()
            if data is not None:
                outs = StringIO ()
                json.dump(data, outs)
                mqtt_client.publish("/" + hostname + "/platform/data", outs.getvalue(), 1, False)
                tpub = time.time()            
              
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        instance = sys.exc_info()
        dp_log.error ("ERROR. Terminating!" + str(instance))



