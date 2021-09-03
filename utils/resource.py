#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_IMAGES = os.path.join(PATH_ROOT, '..', 'images')

images = {}

for name in os.listdir(PATH_IMAGES):
	path = os.path.join(PATH_IMAGES, name)
	with open(path, 'rb') as f:
		images[name] = f.read()
