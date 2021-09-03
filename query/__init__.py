#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List, Dict, NoReturn

from hoshino import Service, R
from hoshino.typing import CQEvent, MessageSegment

import os
import json
import aiofiles
import aiorwlock

from .. import _engines as engines
from . import synthesis

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_FONTS = os.path.join(PATH_ROOT, '..', 'fonts')
PATH_FONT_DEFAULT = os.path.join(PATH_FONTS, 'simhei.ttf')
PATH_CONFIG = os.path.join(PATH_ROOT, 'config.json')

LOCK_CONFIG = aiorwlock.RWLock()

sv = Service('影之诗查卡器', bundle='sv查询', help_='''
[sv_search 关键词 关键词 ...] 进行查卡，支持多关键词
[sv查卡 关键词 关键词 ...] 进行查卡，支持多关键词
[sv_search_engine_list] 列出可用查询引擎
[sv查卡引擎列表] 列出可用查询引擎
[sv_search_engine_set 名称] 设定查询引擎
[sv查卡引擎设定 名称] 设定查询引擎
'''.strip())

def set_default_config(config: Dict={}) -> Dict:
	config.setdefault('engine', 'iyingdi')
	config.setdefault('font', PATH_FONT_DEFAULT)
	config.setdefault('font_size', 16)
	config.setdefault('font_spacing', 4)
	config.setdefault('count_max', 10)
	config.setdefault('line_size_max', 40)
	config.setdefault('card_margin', 8)
	return config

async def load_config() -> Dict:
	if not os.path.isfile(PATH_CONFIG):
		sv.logger.error(f"config file \"{PATH_CONFIG}\" not found")
		return {}
	async with LOCK_CONFIG.reader_lock:
		async with aiofiles.open(PATH_CONFIG, 'r') as f:
			config = json.loads(await f.read())
	return config

async def save_config(config: Dict) -> NoReturn:
	async with LOCK_CONFIG.writer_lock:
		async with aiofiles.open(PATH_CONFIG, 'w') as f:
			await f.write(json.dumps(config))

@sv.on_fullmatch(('sv_search_engine_list', 'sv查卡引擎列表'))
async def sv_search_engine_list(bot, ev: CQEvent):
	await bot.send(ev, '\n'.join([f"引擎: {name}, 源: {source}" for name, source in engines.list_engine()]), at_sender=True)

@sv.on_prefix(('sv_search_engine_set', 'sv查卡引擎设定'))
async def sv_search_engine_set(bot, ev: CQEvent):
	msg = str(ev.message).strip()
	gid = str(ev.group_id)

	if msg not in engines.get_engines():
		await bot.send(ev, f"引擎{msg}不存在", at_sender=True)
		return

	config = await load_config()
	config.setdefault(gid, {})['engine'] = msg
	await save_config(config)

	await bot.send(ev, f"影之诗查卡器引擎变更为{msg}", at_sender=True)

@sv.on_prefix(('sv_search', 'sv查卡'))
async def sv_search(bot, ev: CQEvent):
	msg = str(ev.message).strip()
	uid = str(ev.user_id)
	gid = str(ev.group_id)

	config = await load_config()
	config = config.get(gid, {})
	set_default_config(config)

	e = engines.get_engine(config['engine'])
	filters = list(filter(lambda x: x != '', msg.split(' ')))
	cards = await e.cards_search(filters)

	sv.logger.info(f"find {len(cards)} cards")

	if not cards:
		await bot.send(ev, '没有找到符合条件的卡牌', at_sender=True)
		return

	image_dir = os.path.join('shadowverse', 'query', 'images')
	image_dir_R = R.img(image_dir)
	if not os.path.isdir(image_dir_R.path):
		os.makedirs(image_dir_R.path)
	image_path = os.path.join(image_dir, f"{uid}.png")
	image_path_R = R.img(image_path)

	image = await synthesis.generate_cards_info(cards, config)
	image.save(image_path_R.path)
	image.close()
	await bot.send(ev, f"找到{len(cards)}张卡牌，最多显示{config['count_max']}张卡牌" + image_path_R.cqcode, at_sender=True)
