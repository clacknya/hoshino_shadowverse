#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, TypedDict, NoReturn

import os
import io
import abc
import copy
import aiohttp
import PIL

from . import _base as base
from .. import resource
from hoshino import log, config

class TypeSVGCard(TypedDict):
	name_:       str
	id_:         int
	pp_:         int
	craft_:      str
	rarity_:     str
	type_:       str
	trait_:      str
	expansion_:  str
	baseEffect_: str
	baseFlair_:  str
	rotation_:   bool
	baseAtk_:    int
	baseDef_:    int
	evoAtk_:     int
	evoDef_:     int
	evoEffect_:  str
	evoFlair_:   str
	alts_:       List[int]
	tokens_:     List[int]

class svgdb(base.BaseEngine):

	URL = 'https://svgdb.me/api/en'
	SOURCE = 'svgdb'

	DEFAULT_HEADERS = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
		'Referer':    'https://svgdb.me/carddatabase',
	}

	@classmethod
	async def _fetch_data(cls) -> Dict[str, TypeSVGCard]:
		cls._logger.info(f"fetch: {cls.URL}")
		headers = cls.DEFAULT_HEADERS
		async with aiohttp.ClientSession() as session:
			async with session.get(cls.URL, headers=headers) as response:
				ret = await response.json()
		cls._logger.info(f"fetch: {cls.URL} success")
		return ret


	@classmethod
	def to_std_card(cls, card: TypeSVGCard) -> base.TypeStdCard:
		return {
			'id': str(card.get('id_', '')),
			'names': [
				card.get('name_', ''),
			],
			'descs': [
				card.get('baseFlair_', ''),
			],
			'rules': [
				card.get('baseEffect_', ''),
			],
			'attributes': (
				card.get('_pp', 0),
				card.get('baseAtk_', 0),
				card.get('baseDef_', 0),
			),
			'faction': card.get('craft_'),
			'types': list(filter(
				lambda x: x != '',
				(
					card.get('type_'),
					card.get('trait_'),
				)
			)),
			'series': card.get('expansion_'),
			'rarity': card.get('rarity_'),
			'image': f"https://svgdb.me/assets/fullart/{card.get('id_')}.png",
		}

	@classmethod
	def to_std_cards(cls, cards: Dict[str, TypeSVGCard]) -> List[base.TypeStdCard]:
		return [cls.to_std_card(card) for card in cards.values()]

	# image ----------------------------

	@abc.abstractclassmethod
	def get_std_card_image_url(cls, card: base.TypeStdCard) -> str:
		raise NotImplementedError

	@classmethod
	async def get_std_card_image(cls, card: base.TypeStdCard) -> PIL.Image.Image:
		bytes = io.BytesIO(await cls.get_url(cls.get_std_card_image_url(card)))
		image = PIL.Image.open(bytes).convert("RGBA")
		return image

	@classmethod
	async def get_std_card_images(cls, cards: List[base.TypeStdCard]) -> List[PIL.Image.Image]:
		images = [
			PIL.Image.open(io.BytesIO(bytes)).convert("RGBA") if bytes else \
				PIL.Image.open(io.BytesIO(resource.images['error.png'])).convert("RGBA") \
				for bytes in await cls.get_urls([cls.get_std_card_image_url(card) for card in cards])
		]
		return images

	DEFAULT_IMAGE_CROP_CONFIG = {
		'left':   0.13775,
		'top':    0.19468,
		'right':  0.86381,
		'bottom': 0.86971,
		'wsize':  0.20,
	}
