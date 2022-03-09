#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

import asyncio
import datetime

from . import _base as base
from . import _bagoum
from hoshino import log, config

class bagoum_en(_bagoum.bagoum):

	URL = 'https://sv.bagoum.com/cardsFullJSON/en'
	SOURCE = 'Bagoum EN'

	_logger_name = f"{'.'.join(__name__.split('.')[2:])}@{__qualname__}"
	_logger = log.new_logger(_logger_name, config.DEBUG)

	@classmethod
	def _parse_race(cls, race: str) -> List[str]:
		return race.split(' / ')

	@classmethod
	def _get_image_url_by_id(cls, id: str) -> str:
		return f"https://sv.bagoum.com/cardF/en/c/{id}"

	@classmethod
	def _get_evo_image_url_by_id(cls, id: str) -> str:
		return f"https://sv.bagoum.com/cardF/en/e/{id}"

class bagoum_jp(_bagoum.bagoum):

	URL = 'https://sv.bagoum.com/cardsFullJSON/ja'
	SOURCE = 'Bagoum JP'

	_logger_name = f"{'.'.join(__name__.split('.')[2:])}@{__qualname__}"
	_logger = log.new_logger(_logger_name, config.DEBUG)

	@classmethod
	def _parse_race(cls, race: str) -> List[str]:
		return race.split('\u30fb')

	@classmethod
	def _get_image_url_by_id(cls, id: str) -> str:
		return f"https://sv.bagoum.com/cardF/ja/c/{id}"

	@classmethod
	def _get_evo_image_url_by_id(cls, id: str) -> str:
		return f"https://sv.bagoum.com/cardF/ja/e/{id}"

class bagoum_tw(_bagoum.bagoum):

	URL = 'https://sv.bagoum.com/cardsFullJSON/zh-tw'
	SOURCE = 'Bagoum TW'

	_logger_name = f"{'.'.join(__name__.split('.')[2:])}@{__qualname__}"
	_logger = log.new_logger(_logger_name, config.DEBUG)

	@classmethod
	def _parse_race(cls, race: str) -> List[str]:
		return race.split('\u2027')

	@classmethod
	def _get_image_url_by_id(cls, id: str) -> str:
		return f"https://sv.bagoum.com/cardF/zh-tw/c/{id}"

	@classmethod
	def _get_evo_image_url_by_id(cls, id: str) -> str:
		return f"https://sv.bagoum.com/cardF/zh-tw/e/{id}"
