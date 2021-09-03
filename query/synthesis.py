#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List, Dict

import os
import io
import re
import PIL
import PIL.ImageFont
import PIL.ImageDraw
import itertools
import aiohttp
import asyncio

def get_multiline_textsize(lines: List, font: PIL.ImageFont.FreeTypeFont, spacing: int=4) -> Tuple:
	sizes = [font.getsize(line) for line in lines]
	return (max(sizes)[0], sum(list(zip(*sizes))[1])+spacing*(len(sizes)-1))

def make_text_lines(card: Dict, line_size_max: int=40) -> List[str]:

	def utf8_size(text: str) -> int:
		return int((len(text.encode('UTF-8'))-len(text))/2+len(text))

	def cut(text: str, line_size_max: int) -> List[str]:
		SEPEND = r'[；，。！」]'
		SEP = [
			', ', '\. ', '! ', '; ', '(?=\()', '\) ',
			'，', '、', '；', '—', '……', f'。(?!{SEPEND})', f'！(?!{SEPEND})', '(?=（)', f'）(?!{SEPEND})', '(?=「)', f'」(?!{SEPEND})',
		]
		result = []
		size = utf8_size(text)
		while size > line_size_max:
			seps = list(itertools.chain.from_iterable(map(
				lambda x: [i.end() for i in re.finditer(x, text)],
				SEP
			))) + [len(text)]
			fragment = min([(abs(utf8_size(text[:i])-line_size_max), i) for i in seps])
			result.append(text[:fragment[1]])
			text = text[fragment[1]:]
			size = utf8_size(text)
		if text:
			result.append(text)
		return result

	result = []
	result.extend(card['names'])
	result.append(' ')
	result.append(card['series'])
	result.append(' ')
	result.append('/'.join([card['faction']]+card['varieties']))
	result.append(' ')
	for text in card['descs']:
		for line in text.split('\n'):
			result.extend(cut(line, line_size_max))
	result.append(' ')
	for text in card['rules']:
		for line in text.split('\n'):
			result.extend(cut(line, line_size_max))
	return result

async def generate_cards_info(cards: List[Dict], config: Dict) -> PIL.Image.Image:

	cards = cards[:config['count_max']]

	font = PIL.ImageFont.truetype(
		font=config['font'],
		size=config['font_size'],
		index=0,
		encoding='unic',
		layout_engine=None
	)

	async def fetch(session: aiohttp.client.ClientSession, url: str) -> bytes:
		async with session.get(url) as response:
			return await response.read()

	async with aiohttp.ClientSession() as session:
		card_images = [
			PIL.Image.open(io.BytesIO(image_bytes)).convert("RGBA") \
				for image_bytes in await asyncio.gather(
					*[fetch(session, card['image']) for card in cards]
				)
		]
		card_width_min = min(map(lambda x: x.size[0], card_images))

	text_sections = []
	text_sizes = []

	for card in cards:
		text_lines = make_text_lines(card, config['line_size_max'])
		text_size = get_multiline_textsize(text_lines, font, config['font_spacing'])
		text_sections.append(text_lines)
		text_sizes.append(text_size)

	for card_image in card_images:
		card_image = card_image.thumbnail((card_width_min, card_image.size[1]), PIL.Image.ANTIALIAS)

	card_width_max = card_width_min

	card_margin = config['card_margin']

	image_size = (
		max(map(
			lambda i: card_images[i].size[0] + text_sizes[i][0],
			range(len(cards))
		)) + card_margin * 3,
		sum(map(
			lambda i: max(card_images[i].size[1], text_sizes[i][1]),
			range(len(cards))
		)) + card_margin * (len(cards) + 1)
	)

	image = PIL.Image.new(mode='RGBA', size=image_size, color='white')
	draw = PIL.ImageDraw.Draw(image)

	section_top = card_margin
	for i in range(len(cards)):
		section_height = max(card_images[i].size[1], text_sizes[i][1])
		image.paste(
			im=card_images[i],
			box=(
				int((card_width_max-card_images[i].size[0])/2) + card_margin,
				int((section_height-card_images[i].size[1])/2) + section_top,
			),
			mask=card_images[i]
		)
		text_size = text_sizes[i]
		top = section_top + int((section_height-text_size[1])/2)
		left = card_width_max + card_margin * 2
		text_lines = text_sections[i]
		for text_line in text_lines:
			line_size = font.getsize(text_line)
			draw.text(
				xy=(left, top),
				text=text_line,
				fill='black',
				font=font,
				anchor='la',
				spacing=0,
				align='left',
				# direction=None,
				# features=None,
				# language=None,
				stroke_width=0,
				stroke_fill=None,
				embedded_color=False
			)
			top += line_size[1] + config['font_spacing']
		section_top += section_height + card_margin

	any(map(lambda x: x.close(), card_images))

	return image
