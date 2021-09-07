#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import datetime

from . import _base as base
from . import _svgdb
from hoshino import log, config

class svgdb_en(_svgdb.svgdb):

	URL = 'https://svgdb.me/api/en'
	SOURCE = 'svgdb_en'

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

	@classmethod
	def get_std_card_image_url(cls, card: base.TypeStdCard) -> str:
		return f"https://svgdb.me/assets/cards/en/C_{card.get('id')}.png"

class svgdb_jp(_svgdb.svgdb):

	URL = 'https://svgdb.me/api/jp'
	SOURCE = 'svgdb_jp'

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

	@classmethod
	def get_std_card_image_url(cls, card: base.TypeStdCard) -> str:
		return f"https://svgdb.me/assets/cards/jp/C_{card.get('id')}.png"
