#!/usr/bin/env python3

'''
Created on January 2012
@author: tufan
@description: publishes given coordinates to mqtt and terminates

@pub: /<hostname>/crsspd/prop/data
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
from io import StringIO
import json
import paho.mqtt.client as mqtt

import log

dp_log = log.dp_log

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
    parser = argparse.ArgumentParser (prog="cl_propCrsSpdUpdate", description="Publishes given course and / or speed proposal")
    parser.add_argument ("-t", "--host", dest="host", action="store", default="localhost", help="MQTT broker hostname")
    parser.add_argument ("-p", "--port", dest="port", action="store", default="1883", help="MQTT broker port")

    parser.add_argument ("-c", "--course", dest="course", action="store", help="Platform course (0.0, 359.9) in degrees")
    parser.add_argument ("-s", "--speed", dest="speed", action="store", help="Platform speed (=>0.0 in kts")

    args = parser.parse_args()

    if (not args.course and not args.speed):
        dp_log.error ("Either course or speed, or both must be given")
        raise SystemExit
    
    data = {'datetime':time.time()}
    if (args.course):
        data['course'] = float(args.course)
        
    if (args.speed):
        data['speed'] = float(args.speed)
        
    dp_log.debug (repr(data))
    
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

    
    outs = StringIO ()
    json.dump(data, outs)
    
    topic = "/" + hostname + "/crsspd/prop/data"

    dp_log.debug("Shall publish " + topic + " with value '" + outs.getvalue() + "'")
    
    mqtt_client.publish(topic, outs.getvalue(), 1, True)
    
    mqtt_client.loop_forever()
    
    dp_log.debug("Done!")
   
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        instance = sys.exc_info()
        dp_log.error ("ERROR. Terminating!" + str(instance))

