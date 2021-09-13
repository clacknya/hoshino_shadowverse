#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, TypedDict

import abc
import lxml.html

from . import _base as base

class TypeBagoumBaseData(TypedDict):
	description: str
	flair:       str
	attack:      int
	defense:     int

class TypeBagoumEvoData(TypedDict):
	description: str
	flair:       str
	attack:      int
	defense:     int

class TypeBagoumCard(TypedDict):
	name:           str
	_name:          str
	id:             str
	faction:        str
	_faction:       str
	rarity:         str
	_rarity:        str
	race:           str
	expansion:      str
	_expansion:     str
	type:           str
	hasEvo:         bool
	hasAlt:         bool
	hasAlt2:        bool
	manaCost:       int
	baseData:       TypeBagoumBaseData
	evoData:        TypeBagoumEvoData
	rot:            str
	searchableText: str

class bagoum(base.BaseEngine):

	URL = 'https://sv.bagoum.com/cardsFullJSON/en'
	SOURCE = 'Bagoum'

	DEFAULT_HEADERS = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
		'Referer':    'https://sv.bagoum.com/cardSort',
	}

	@classmethod
	async def _fetch_data(cls) -> Dict[str, TypeBagoumCard]:
		cls._logger.info(f"fetch data")
		headers = cls.DEFAULT_HEADERS
		ret = await cls._get_url_json(cls.URL, headers=headers)
		cls._logger.info(f"fetch data succeed")
		return ret

	@classmethod
	def _parse_race(cls, race: str) -> List[str]:
		return [race]

	@classmethod
	def to_std_card(cls, card: TypeBagoumCard) -> base.TypeStdCard:
		return {
			'id': card.get('id', ''),
			'names': [
				card.get('name', ''),
			],
			'faction': card.get('faction'),
			'types': list(filter(
				lambda x: x not in [''],
				(
					card.get('type'),
					*cls._parse_race(card.get('race', '')),
				)
			)),
			'series': card.get('expansion'),
			'rarity': card.get('rarity'),
			'descs': card.get('baseData', {}).get('flair', '').split('<br>'),
			'rules': card.get('baseData', {}).get('description', '').split('<br>'),
			'attributes': (
				card.get('manaCost', 0),
				card.get('baseData', {}).get('attack', 0),
				card.get('baseData', {}).get('defense', 0),
			),
			# 'image': f"https://sv.bagoum.com/getRawImage/0/0/{card.get('id')}/s",
			'image': cls._get_image_url_by_id(card.get('id')),
			'evo_descs': card.get('evoData', {}).get('flair', '').split('<br>'),
			'evo_rules': card.get('evoData', {}).get('description', '').split('<br>'),
			'evo_attributes': (
				card.get('manaCost', 0),
				card.get('evoData', {}).get('attack', 0),
				card.get('evoData', {}).get('defense', 0),
			),
			'evo_image': cls._get_evo_image_url_by_id(card.get('id')),
		}

	@classmethod
	def to_std_cards(cls, cards: Dict[str, TypeBagoumCard]) -> List[base.TypeStdCard]:
		return [cls.to_std_card(card) for card in cards.values()]

	# image ----------------------------

	@abc.abstractclassmethod
	def _get_image_url_by_id(cls, id: str) -> str:
		raise NotImplementedError

	@abc.abstractclassmethod
	def _get_evo_image_url_by_id(cls, id: str) -> str:
		raise NotImplementedError

	DEFAULT_IMAGE_CROP_CONFIG = {
		'left':   0.13619,
		'top':    0.19466,
		'right':  0.86349,
		'bottom': 0.86945,
		'wsize':  0.20,
	}

	# voice ----------------------------

	@classmethod
	async def get_std_card_voices(cls, card: base.TypeStdCard) -> base.TypeStdCardVoices:
		url = f"https://sv.bagoum.com/cards/{card['id']}"
		text = await cls._get_url_text(url, headers=cls.DEFAULT_HEADERS)

		html = lxml.html.fromstring(text)
		nodes = html.cssselect('.voiceTable > tbody > tr')

		if len(nodes) == 0:
			return []

		nodes.pop(0)
		result = []
		for node in nodes:
			children = node.getchildren()
			sources = node.cssselect('source')
			result.append({
				'action': children[0].text.strip(),
				'voice':  f"https://sv.bagoum.com{sources[0].get('src')}",
			})

		return result
