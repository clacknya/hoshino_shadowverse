#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union, List, Dict, NoReturn

import abc
import json
import aiofiles

class BaseEngine():

	@classmethod
	async def save_json(cls, path: str, data: Union[List, Dict]) -> NoReturn:
		async with aiofiles.open(path, 'w') as f:
			await f.write(json.dumps(data))

	@classmethod
	async def load_json(cls, path: str) -> Union[List, Dict]:
		async with aiofiles.open(path, 'r') as f:
			return json.loads(await f.read())

	@classmethod
	def rarity_calc(cls, rarity: str) -> int:
		rarity = rarity.lower()
		if rarity in [
			'bronze', '铜', '青铜',
		]:
			return 0
		if rarity in [
			'silver', '银', '白银',
		]:
			return 1
		if rarity in [
			'gold', '金', '黄金',
		]:
			return 2
		if rarity in [
			'legendary', '虹', '传说',
		]:
			return 3
		return -1

	@abc.abstractclassmethod
	async def cards_search(cls, filters: List[str]) -> List[Dict]:
		raise NotImplementedError
