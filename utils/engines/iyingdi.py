#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, NoReturn

import os
import sys
import re
import asyncio
import datetime

from . import _base as base
from hoshino import log, config

class iyingdi(base.BaseEngine):

	URL = 'https://api2.iyingdi.com/verse/card/search/vertical'
	SOURCE = '旅法师营地'

	DEFAULT_HEADERS = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
		'Referer':    'https://www.iyingdi.com/',
	}

	_logger_name = f"{'.'.join(__name__.split('.')[2:])}@{__qualname__}"
	_logger = log.new_logger(_logger_name, config.DEBUG)

	_data = None
	_data_lock = asyncio.Lock()
	_data_expire_date = datetime.datetime.min
	_data_update_cd = datetime.timedelta(hours=24)

	_std_data = None
	_std_data_lock = asyncio.Lock()
	_std_data_expire_date = datetime.datetime.min
	_std_data_update_cd = datetime.timedelta(hours=24)

	# only for debug, lock is required for use
	@classmethod
	async def _save_data(cls, path: str) -> NoReturn:
		cls._logger.info(f"save data to: {path}")
		await cls.save_json(path, cls._data)

	# only for debug, lock is required for use
	@classmethod
	async def _load_data(cls, path: str) -> List[Dict]:
		cls._logger.info(f"load data from: {path}")
		cls._update_data(await cls.load_json(path))
		return cls._data

	@classmethod
	async def _fetch_data(cls) -> List[Dict]:
		cls._logger.info(f"fetch data")
		headers = cls.DEFAULT_HEADERS
		data = {
			'statistic': 'total',
			'token':     '',
			'page':      '0',
			'size':      '0',
			'collect':   '0',
			'envolve':   '0',
		}
		ret = await cls._post_url_json(cls.URL, headers=headers, data=data)
		if ret.get('success', False):
			cls._logger.info(f"fetch data succeed")
			return ret.get('data', {}).get('cards', [])
		else:
			cls._logger.error(f"fetch data failed")
			return []

	@classmethod
	def to_std_card(cls, card: Dict) -> base.TypeStdCard:
		return {
			'id': card.get('gameid', ''),
			'names': [
				card.get('cname', ''),
				# card.get('jname', ''),
				# card.get('ename', ''),
			],
			'faction': card.get('faction'),
			'types': list(filter(
				lambda x: x != '',
				(
					card.get('mainType'),
					card.get('subType'),
				)
			)),
			'series': card.get('seriesName'),
			'rarity': card.get('rarity'),
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
			'attributes': (
				card.get('mana', 0),
				card.get('attack', 0),
				card.get('hp', 0),
			),
			'image': card.get('img'),
			'evo_descs': [
				'',
			],
			'evo_rules': [
				'',
			],
			'evo_attributes': (
				0,
				0,
				0,
			),
			'evo_image': '',
		}

	@classmethod
	def to_std_cards(cls, cards: List[Dict]) -> List[base.TypeStdCard]:
		return [cls.to_std_card(card) for card in cards]

	# image ----------------------------

	DEFAULT_IMAGE_CROP_CONFIG = {
		'left':   0.13775,
		'top':    0.19468,
		'right':  0.86381,
		'bottom': 0.86971,
		'wsize':  0.20,
	}
