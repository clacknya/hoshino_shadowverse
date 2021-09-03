#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, NoReturn

import re
import aiohttp
import datetime

from . import _base as base

class iyingdi(base.BaseEngine):

	URL = 'https://api2.iyingdi.com/verse/card/search/vertical'
	SOURCE = '国服'

	@classmethod
	async def save_vertical(cls, path: str) -> NoReturn:
		await cls.save_json(path, cls.vertical)

	@classmethod
	async def load_vertical(cls, path: str) -> List[Dict]:
		cls.vertical = await cls.load_json(path)
		cls.cdtime = datetime.datetime.now() + datetime.timedelta(hours=23)
		return cls.vertical

	@classmethod
	async def fetch_vertical(cls) -> List[Dict]:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
		}
		data = {
			'statistic': 'total',
			'token':     '',
			'page':      '0',
			'size':      '0',
			'collect':   '0',
			'envolve':   '0',
		}
		async with aiohttp.ClientSession() as session:
			async with session.post(cls.URL, headers=headers, data=data) as response:
				ret = await response.json(content_type=None)
		if ret.get('success', False):
			return ret.get('data', {}).get('cards', [])
		else:
			return []

	@classmethod
	async def get_vertical(cls) -> List[Dict]:
		if (not hasattr(cls, 'vertical')) or \
			(not hasattr(cls, 'cdtime')) or \
			(datetime.datetime.now() > cls.cdtime):
			cls.vertical = await cls.fetch_vertical()
			cls.cdtime = datetime.datetime.now() + datetime.timedelta(hours=23)
		return cls.vertical

	@classmethod
	def reduce_cards_data(cls, cards: List[Dict], filter: str) -> List[Dict]:
		result = []
		if re.match(r'^\d+$', filter):
			for card in cards:
				ability = str(card.get('mana')) + str(card.get('attack')) + str(card.get('hp'))
				if ability == filter:
					result.append(card)
		else:
			for card in cards:
				if filter in card.get('cname', '') or \
					filter in card.get('jname', '') or \
					filter in card.get('ename', '') or \
					filter in card.get('crule', '') or \
					filter in card.get('jrule', '') or \
					filter in card.get('erule', '') or \
					card.get('faction') == filter or \
					card.get('mainType') == filter or \
					card.get('subType') == filter or \
					card.get('seriesName') == filter or \
					cls.rarity_calc(card.get('rarity')) == cls.rarity_calc(filter):
					result.append(card)
		return result

	@classmethod
	def get_std_cards(cls, cards: List[Dict]) -> List[Dict]:
		return [
			{
				'id': card.get('gameid', ''),
				'names': [
					card.get('cname', ''),
					# card.get('jname', ''),
					# card.get('ename', ''),
				],
				'descs': [
					card.get('cdesc', ''),
					# card.get('jdesc', ''),
					# card.get('edesc', ''),
				],
				'rules': [
					card.get('crule', ''),
					# card.get('jrule', ''),
					# card.get('erule', ''),
				],
				'ability': (
					card.get('mana'),
					card.get('attack'),
					card.get('hp'),
				),
				'faction': card.get('faction'),
				'varieties': list(filter(
					lambda x: x != '',
					(
						card.get('mainType'),
						card.get('subType'),
					)
				)),
				'series': card.get('seriesName'),
				'rarity': card.get('rarity'),
				'image': card.get('img'),
			} for card in cards
		]

	@classmethod
	async def cards_all(cls) -> List[Dict]:
		cards = await cls.get_vertical()
		return cls.get_std_cards(cards)

	@classmethod
	async def cards_search(cls, filters: List[str]) -> List[Dict]:
		cards = await cls.get_vertical()
		for f in filters:
			cards = cls.reduce_cards_data(cards, f)
		return cls.get_std_cards(cards)
