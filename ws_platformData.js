#!/usr/bin/env node
/* *
 * ws_platformData.js
 * 
 * $Id$
 * 
 * a node mqtt client and ws server
 * - consumes platformData and 
 * - updates connected web clients through faye pub/sub framework
 * 
 */

const util = require('util'),
	http = require('http'),
	faye = require('faye'),
	mqtt = require('mqtt');

var mqhost = 'mqtt://localhost:1883', // subscribes mqtt broker to get /+/platform/data 
	aliveTimeout = 60, // seconds
	bxserver = http.createServer(),   // servs platform data to faye clients like browsers 
	bxport = 4023,
	topic = '/+/platform/data';

var bayeux = new faye.NodeAdapter({mount: '/mqtt'}); 

// initialize and define mqtt client callbacks

const mqclient = mqtt.connect(mqhost, {'keepalive' : aliveTimeout});

mqclient.on('connect', function(packet) {
	if (packet.returnCode === 0) {
		console.log("subscribing to mqtt topic " + topic)
		mqclient.subscribe(topic);
	} else {
		console.log('connack error %d', packet.returnCode);
		process.exit(-1);
	}
});

// var keepAliveID = setInterval(function(){
// 	mqclient.pingreq();
// }, 
// aliveTimeout / 2);

mqclient.on('message', function(topic, message, packet) {
	console.log('%s\t%s', topic, message);
	bayeux.getClient().publish('/platform/data', message.toString())
	bayeux.getClient().publish('/platform/state', 'Operational')
	bayeux.getClient().publish()
	clearInterval (intervalID);
	intervalID = setInterval(function(){
		bayeux.getClient().publish('/platform/state', 'Connected')
	}, 
	10000);
});

mqclient.on('close', function() {
	bayeux.getClient().publish('/platform/state','Offline')
	process.exit(0);
});

mqclient.on('error', function(e) {
	bayeux.getClient().publish('/platform/state','Error')
	console.log('error %s', e);
	process.exit(-1);
});

bayeux.bind('handshake', function(clientId) {
	console.log('Client connected with id ' + clientId)
})

// ws /platform/state server

bayeux.bind('subscribe', function(clientId, topic) {
	console.log(clientId + ' subscribed to ' + topic)
})

bayeux.bind('disconnect', function(clientId) {
	console.log(clientId + ' disconnected!')
})

var intervalID = setInterval(function(){
	bayeux.getClient().publish('/platform/state','Connected')
}, 
10000);

// start to serve ws cliens like browsers

bayeux.attach(bxserver);
bxserver.listen(bxport)

console.log ('PlatformData feeder running at '+bxport);

