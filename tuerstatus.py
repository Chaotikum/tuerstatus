#!/usr/bin/env python

import json
import os
import requests

from mpd import MPDClient

LOCK = '334EC1'
URL = 'http://localhost/status/door'

MPD_HOST = os.environ['MPD_HOST']
MPD_PORT = os.environ['MPD_PORT']
MPD_PASS = os.environ['MPD_PASS']

open_last = False

lights = [8, 7, 6, 5, 4, 3, 1]

def handleMPD(is_open):
	if not is_open:
		print ("Pausing MPD")
		client = MPDClient()
		client.connect(MPD_HOST, MPD_PORT)
		client.password(MPD_PASS)

		client.pause(1)

		client.close()
		client.disconnect()

def handleStateChange(is_open):
	handleMPD(is_open)
	payload = {'door_open': 1 if is_open else 0}
	print("Payload ", payload)
	for x in range(1,5):
		r = requests.post(URL, data=payload)
		print(r)

		if r.status_code == requests.codes.ok:
			break

	if not is_open:
		for x in lights:
			url = "http://troll.nobreakspace.org/control?cmd=set_state_actuator&number={0}&function=2".format(x)
			requests.get(url)

while True:
	r = requests.get('https://padlock.nobreakspace.org/api/locks/stream', cert=('tuerstatus.crt', 'tuerstatus.key'), stream=True, verify=False)

	for line in r.iter_lines(chunk_size=16):
		print("Result line ", line)
		if len(line) > 3:
			data = line[6:]
			data = json.loads(data.decode("UTF-8"))
			locks = dict()
			for d in data:
				locks[d['id']] = d

			# print("Locks data", locks)

			is_open = not locks[LOCK]['locked']
			if open_last != is_open:
				open_last = is_open

				handleStateChange(is_open)
