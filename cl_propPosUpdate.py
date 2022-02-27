#!/usr/bin/env python3

'''
Created on January 2012
@author: tufan
@description: publishes given coordinates to mqtt and terminates

@pub: /<hostname>/pos/prop/data
@sub:
@pubsub:
'''

__version__ = "$Id$"

import os
import sys
import time
import platform
import argparse
import getpass
import operator
import logging
from io import StringIO
import json
import paho.mqtt.client as mqtt

import log

dp_log = log.dp_log

def get_positions (position):
    
    if len(position) != 2:
        dp_log.error("Not enough position values!")
        raise SystemExit
    
    vala = position[0].upper()
    valb = position[1].upper()
    
    if ('[E|W|N|S]'.find(vala[-1]) == -1):
        dp_log.error("Position must be N, S, E or W!")
        raise SystemExit
        
    if ('[E|W|N|S]'.find(valb[-1]) == -1):
        dp_log.error("Position must be N, S, E or W!")
        raise SystemExit
       
    if (('[E|W]'.find(vala[-1]) != -1) and ('[E|W]'.find(valb[-1]) != -1)):
        dp_log.error("Both values are longitude. One must be latitude!")
        raise SystemExit
 
    if (('[N|S]'.find(vala[-1]) != -1) and ('[N|S]'.find(valb[-1]) != -1)):
        dp_log.error("Both values are latitude. One must be longitude!")
        raise SystemExit

    poslat = 0.0
    poslong = 0.0
    
    if ('[N|S]'.find(vala[-1]) != -1):
        poslat = float(vala[:-1])
        if 'S' in vala[-1]:
            poslat = operator.neg(poslat)
            
        poslong = float(valb[:-1])
        if 'W' in valb[-1]:
            poslong = operator.neg(poslong)

    else:
        poslat = float(valb[:-1])
        if 'S' in valb[-1]:
            poslat = operator.neg(poslat)
            
        poslong = float(vala[:-1])
        if 'W' in vala[-1]:
            poslong = operator.neg(poslong)
        
    if abs(poslat) > 90.0:
        dp_log.error("Latitude cannot be greater then 90.0 degrees")
        raise SystemExit
    
    if abs(poslong) > 180.0:
        dp_log.error("Longitude cannot be greater then 180.0 degrees")
        raise SystemExit

    return poslat, poslong


def on_connect(client, userdata, flgs, rc):
    if rc == 0:
        dp_log.debug ("Connected successfully with result code " + str(rc))
    else:
        dp_log.error ("Broker error! Cannot connect!")
        raise SystemExit

    
def on_publish(clinet, user_data, mid):
    dp_log.debug ("Published successfully!")
    clinet.disconnect()


def on_disconnect(clinet, user_data, rc):
    dp_log.debug("Disconnected successfully.")

    
def main():
    parser = argparse.ArgumentParser (prog="cl_propPosUpdate", description="Publishes given position data")
    parser.add_argument ("-t", "--host", dest="host", action="store", default="localhost", help="MQTT broker hostname")
    parser.add_argument ("-p", "--port", dest="port", action="store", default="1883", help="MQTT broker port")
    parser.add_argument ("position", nargs=2, help="Platform Lat Long in the form of #.#[N|S] #.#[E|W]")

    args = parser.parse_args()

    dp_log.debug (args.host + ', ' + args.port + ', ' + ','.join(args.position))

    poslat, poslong = get_positions(args.position)

    cname = os.path.basename(sys.argv[0])
    hostname = platform.node().split('.')[0]
    username = getpass.getuser()

    mqtt_client = mqtt.Client(username + '@' + hostname + ':' + cname)
    
    mqtt_client.on_connect = on_connect 
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_publish = on_publish

    result = mqtt_client.connect(host=args.host, port=int(args.port), keepalive=10) 

    if (result != 0):
        dp_log.error ("Error connecting to mqtt broker!")
        raise SystemExit

    data = {'datetime':time.time(), 'latitude':poslat, 'longitude':poslong}
    
    outs = StringIO ()
    json.dump(data, outs)
    
    topic = "/" + hostname + "/pos/prop/data"
    
    dp_log.debug("Shall publish " + topic + " with value '" + outs.getvalue() + "'")
    
    mqtt_client.publish(topic, outs.getvalue(), 1, True)    
    
    mqtt_client.loop()
    
    dp_log.debug("Done!")
   
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        instance = sys.exc_info()
        dp_log.error ("ERROR. Terminating!" + str(instance))

