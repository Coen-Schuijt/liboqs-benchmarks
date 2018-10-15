#!/usr/bin/env python3

import os

def connect():
	os.system("docker exec -i -t benchmark-container bash")
	return

if __name__ == "__main__":
	connect()
