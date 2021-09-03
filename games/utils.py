#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List, Dict

import io
import re
import PIL
import random
import aiohttp

punctuation = (
	'\uFF02\uFF03\uFF04\uFF05\uFF06\uFF07\uFF08\uFF09\uFF0A\uFF0B\uFF0C\uFF0D'
	'\uFF0F\uFF1A\uFF1B\uFF1C\uFF1D\uFF1E\uFF20\uFF3B\uFF3C\uFF3D\uFF3E\uFF3F'
	'\uFF40\uFF5B\uFF5C\uFF5D\uFF5E\uFF5F\uFF60'
	'\uFF62\uFF63\uFF64'
	'\u3000\u3001\u3003'
	'\u3008\u3009\u300A\u300B\u300C\u300D\u300E\u300F\u3010\u3011'
	'\u3014\u3015\u3016\u3017\u3018\u3019\u301A\u301B\u301C\u301D\u301E\u301F'
	'\u3030'
	'\u303E\u303F'
	'\u2013\u2014'
	'\u2018\u2019\u201B\u201C\u201D\u201E\u201F'
	'\u2026\u2027'
	'\uFE4F'
	'\uFE51\uFE54'
	'\u00B7'
	'\uFF01'
	'\uFF1F'
	'\uFF61'
	'\u3002'
)

def get_name_match_pattern(card: Dict) -> re.Pattern:
	names = []
	for name in card['names']:
		for symbol in punctuation:
			if symbol not in '.?':
				name = name.replace(symbol, '.?')
		names.append(name)
	return re.compile('|'.join(names))

def crop_card_image(image: PIL.Image.Image, config: Dict) -> PIL.Image.Image:
	x0 = int(image.size[0] * config['left'])
	y0 = int(image.size[1] * config['top'])
	ws = int(image.size[1] * config['wsize'])
	x1 = int(image.size[0] * config['right']) - ws
	y1 = int(image.size[0] * config['bottom']) - ws
	x2 = random.randint(x0, x1)
	y2 = random.randint(y0, y1)
	return image.crop((x2, y2, x2 + ws, y2 + ws))

async def get_card_image(card: Dict, config: Dict) -> PIL.Image.Image:
	async with aiohttp.ClientSession() as session:
		async with session.get(card['image']) as response:
			image = PIL.Image.open(io.BytesIO(await response.read())).convert("RGBA")
	return image

def get_random_card(cards: List[Dict], config: Dict) -> Dict:
	return random.choice(cards)
