#!/usr/bin/env python

import json
import requests

LOCK = '334EC1'
URL = 'http://localhost/status/door'

open_last = False

lights = [5, 4, 3, 1]

while True:
	r = requests.get('https://padlock.nobreakspace.org/api/locks/stream', cert=('tuerstatus.crt', 'tuerstatus.key'), stream=True, verify=False)

	for line in r.iter_lines(chunk_size=16):
		print("line", line)
		if len(line) > 3:
			data = line[6:]
			data = json.loads(data.decode("UTF-8"))
			locks = dict()
			for d in data:
				locks[d['id']] = d

			print(locks)

			is_open = not locks[LOCK]['locked']
			if open_last != is_open:
				open_last = is_open

				payload = {'door_open': 1 if is_open else 0}
				print("payload", payload)
				for x in range(1,5):
					r = requests.post(URL, data=payload)
					print(r)

					if r.status_code == requests.codes.ok:
						break

				if not is_open:
					for x in lights:
						url = "http://troll.nobreakspace.org/control?cmd=set_state_actuator&number={0}&function=2".format(x)
						requests.get(url)

