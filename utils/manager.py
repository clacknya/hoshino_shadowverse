#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union, Any, List, Dict, NoReturn

import os
import json
import copy
import logging
import aiofiles
import aiorwlock

from hoshino import log, config

class Manager():

	def __init__(self):
		self._logger_name = f"{'.'.join(__name__.split('.')[2:])}@{self.__class__.__name__}"
		self._logger = log.new_logger(self._logger_name, config.DEBUG)

class ConfigManager(Manager):

	def __init__(self, path: str):
		super().__init__()
		self._path = path
		self._lock = aiorwlock.RWLock()

	async def load(self, default_value: Union[List, Dict]={}) -> Union[List, Dict]:
		if not os.path.isfile(self._path):
			self._logger.warning(f"config file \"{self._path}\" not found")
			return default_value
		async with self._lock.reader_lock:
			async with aiofiles.open(self._path, 'r') as f:
				config = json.loads(await f.read())
		self._logger.info(f"config file \"{self._path}\" loaded")
		return config

	async def save(self, config: Union[List, Dict]) -> NoReturn:
		async with self._lock.writer_lock:
			async with aiofiles.open(self._path, 'w') as f:
				await f.write(json.dumps(config))
		self._logger.info(f"config file \"{self._path}\" saved")

class GameManager(Manager):

	def __init__(self, name: str):
		super().__init__()
		self._idle = {}
		self._name = name
		self._data = {}
		self._winner = {}
		# > 0: winner qq
		# = 0: winner undetermined
		# < 0: error code (like reach time limit)

	def get_data(self, gid: int) -> Any:
		return copy.deepcopy(self._data.get(gid))

	def set_data(self, gid: int, data: Any) -> NoReturn:
		self._data[gid] = copy.deepcopy(data)

	def is_idle(self, gid: int) -> bool:
		return self._idle.get(gid, True)

	def is_data_set(self, gid: int) -> bool:
		return self._data.get(gid) != None

	def start(self, gid: int) -> NoReturn:
		self._idle[gid] = False
		self._winner[gid] = 0
		self._data[gid] = None

	def win(self, gid: int, winner: int) -> NoReturn:
		self._winner[gid] = winner

	def finish(self, gid: int) -> NoReturn:
		self._idle[gid] = True

	def get_winner(self, gid: int) -> int:
		return self._winner.get(gid, 0)

	def get_player_info(player: int) -> Dict:
		raise NotImplementedError
