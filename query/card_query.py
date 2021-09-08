#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List, Dict, NoReturn

from hoshino import Service, R
from hoshino.typing import CQEvent, MessageSegment

import os

from ..utils import engine
from ..utils import manager

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_FONTS = os.path.join(PATH_ROOT, '..', 'fonts')
PATH_FONT_DEFAULT = os.path.join(PATH_FONTS, 'simhei.ttf')
PATH_CONFIG = os.path.join(PATH_ROOT, 'config.json')

NAME_MODULE = __name__.split('.')[-1]

cfgmgr = manager.ConfigManager(PATH_CONFIG)

sv = Service('影之诗查卡器', bundle='sv查询', help_='''
[sv查卡 关键词 关键词 ...] 进行查卡，支持多关键词
'''.strip())
# [sv查卡引擎列表] 列出可用查询引擎
# [sv查卡引擎设定 名称] 设定查询引擎

def set_default_config(config: Dict={}) -> Dict:
	config.setdefault('engine', 'iyingdi')
	config.setdefault('font', PATH_FONT_DEFAULT)
	config.setdefault('font_size', 16)
	config.setdefault('font_spacing', 4)
	config.setdefault('count_max', 10)
	config.setdefault('line_size_max', 40)
	config.setdefault('card_margin', 16)
	return config

@sv.on_fullmatch(('sv查卡引擎列表', ))
async def sv_search_engine_list(bot, ev: CQEvent):
	await bot.send(ev, '\n'.join([f"引擎: {name}, 源: {source}" for name, source in engine.list_engines()]), at_sender=True)

@sv.on_prefix(('sv查卡引擎设定', ))
async def sv_search_engine_set(bot, ev: CQEvent):
	msg = ev.message.extract_plain_text()
	gid = str(ev.group_id)

	if msg not in engine.get_engines():
		await bot.send(ev, f"引擎 {msg} 不存在", at_sender=True)
		return

	config = await cfgmgr.load({})
	config.setdefault(gid, {}).setdefault(NAME_MODULE, {})['engine'] = msg
	await cfgmgr.save(config)

	await bot.send(ev, f"影之诗查卡器引擎变更为 {msg}", at_sender=True)

@sv.on_prefix(('sv查卡', ))
async def sv_search(bot, ev: CQEvent):
	msg = ev.message.extract_plain_text()
	uid = str(ev.user_id)
	gid = str(ev.group_id)

	filters = list(filter(lambda x: x != '', msg.split(' ')))

	sv.logger.debug(f"filters: {filters}")

	config = await cfgmgr.load({})
	config = config.get(gid, {}).get(NAME_MODULE, {})
	set_default_config(config)

	await bot.send(ev, f"使用引擎 {config['engine']} 进行查找", at_sender=False)

	eg = engine.get_engine(config['engine'])

	try:
		cards = await eg.search_std_cards(filters)
	except NotImplementedError as e:
		sv.logger.critical(f"{e}")
		await bot.finish(ev, '该引擎功能未实现')
	except Exception as e:
		sv.logger.critical(f"{e}")
		await bot.finish(ev, '获取卡牌资源出错…')

	sv.logger.info(f"find {len(cards)} cards")

	if not cards:
		await bot.send(ev, '没有找到符合条件的卡牌', at_sender=True)
		return

	image_dir = os.path.join('shadowverse', 'query', 'images')
	image_path = os.path.join(image_dir, f"{uid}.png")
	image_res = R.img(image_path)
	os.makedirs(R.img(image_dir).path, exist_ok=True)

	image = await eg.generate_std_cards_info_image(cards, config)
	image.save(image_res.path)
	image.close()

	await bot.send(ev, f"找到{len(cards)}张卡牌，最多显示{config['count_max']}张卡牌{image_res.cqcode}", at_sender=True)
