# Platform Data

This is a simple technology demonstration work that utilizes [mqtt](https://mqrr.org) and [faye](https://faye.jcoglan.com) framework that uses [bayeux](https://faye.jcoglan.com) pub/sub frameworks to distribute platform data that is composed of position, course and speed.

When platform data (position, course and speed) exists (published) in the system   platform position advances (dead reconning) and new position information is published to the (web) subscribers.

You can use any mqtt broker. I used opensource [mosquitto](https://mosquitto.org).

## Requirements

- mqtt broker (like mosquitto)
- python3
  - paho-mqtt (pyton mqtt library)
  - pyproj (python projection library)
- node
  - mqtt.js
  - faye (js)
- modern web browser
  - jquery*.js
  - bootstrap*.js | css
  - faye-browser*.js
  - geodesys.js

## pub/sub topics

topic | value | note
---|---|---|
/[src]/pos/prop/data |  {'datatime': time from epoch, 'longitude' : 0..180EW, 'latitude' : 0..90NS} | platform position in latitude and longitude  
/[src]/crsspd/prop/data | {'datatime': time from epoch, 'course' : 0..360, 'speed' : >0 } | platform course and speed
/[src]/platform/data | {latitude": 0.0, "longitude": 0.0, "course": 0.0, "speed": 0.0, "timeval": time from epoch | platform information calculated by the provider  
/[src]/platform/state | 'Operational' or 'Connected' or 'Offline' or 'Error' | platform data provider state

## Files

file | usage | note
---|---|---|
`./cl_propCrsSpdUpdate.py` | -h flag provides the usage | publishes course and speed topic (`/[src]/crsspd/prop/data`) with the values provided from the command line and terminate. This script is used to provide the initial or updated course speed data to the dead reconning service (`dp_platformDataUpdate.py`).
`./cl_propPosUpdate.py` | -h flag provides the usage | publishes position topic (`/[src]/pos/prop/data`) with the values provided from the command line and terminate. This script is used to provide initial or updated positiın data to the dead reconning service (`dp_platformDataUpdate.py`).
`./dp_platformDataUpdate.py`| -h flag provides the usage | "dead reconning" service. Consumes `/+/+/prop/data` data, periodically calculates and publishes platform data (`/+/platform/data`).
`./ws_platformData.js`| | a simple node server that subscribes `/+/platform/data` mqtt topic and publishes `/platform/data` and `/platform/status` topics to the web subscribers using faye framework.
`Web/platformdata.html` | | Web client that consumes `/platform/data` and `/platform/status` through faye pub/sub frame.

## How to run

Assuming you have installed prerequisite applications and modules, simply run the applications as follows.

1. start mqtt broker (`% mosquitto -v`)
2. start platform daya service (`% python3 ./dp_platformDataUpdate.py`)
3. start web client (browser) platform data broker (`%node ./ws_platformData.js`)
4. open platform.html page with your browser
5. produce platform location data (`% python3 ./cl_propPosUpdate.py  12N 23W`)
6. produce platform course and speed data (`% python3 ./cl_propCrsSpdUpdate.py -c 47 -s 22`)

observe platform data change in platform.html page. You may need to refresh the page to trigger web client to subscribe platform data. You can open as many platform.html pages and observe all of them are updated at once.
