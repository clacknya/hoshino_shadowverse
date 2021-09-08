#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Type, Union, Dict, NoReturn

from hoshino import Service, R, util
from hoshino.typing import CQEvent, MessageSegment

import os
import asyncio

from ..utils import engine
from ..utils import manager

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_CONFIG = os.path.join(PATH_ROOT, 'config.json')

NAME_MODULE = __name__.split('.')[-1]

cfgmgr = manager.ConfigManager(PATH_CONFIG)
gmmgr = manager.GameManager(NAME_MODULE)

sv = Service('影之诗猜卡牌', bundle='sv娱乐', help_='''
[sv猜卡牌 关键词 关键词 ...] 进行猜卡牌游戏，可选关键词筛选
'''.strip())
# [sv猜卡牌解锁] 当猜卡牌游戏超时限未自动结束死锁时解锁
# [sv猜卡牌引擎列表] 列出可用查询引擎
# [sv猜卡牌引擎设定 名称] 设定查询引擎

def set_default_config(config: Dict={}) -> Dict:
	config.setdefault('engine', 'iyingdi')
	config.setdefault('time_limit', 30)
	return config

@sv.on_fullmatch(('sv猜卡牌引擎列表', ))
async def sv_card_guess_engine_list(bot, ev: CQEvent):
	await bot.send(ev, '\n'.join([f"引擎: {name}, 源: {source}" for name, source in engine.list_engines()]), at_sender=True)

@sv.on_prefix(('sv猜卡牌引擎设定', ))
async def sv_card_guess_engine_set(bot, ev: CQEvent):
	msg = ev.message.extract_plain_text()
	gid = str(ev.group_id)

	if msg not in engine.get_engines():
		await bot.send(ev, f"引擎 {msg} 不存在", at_sender=True)
		return

	config = await cfgmgr.load({})
	config.setdefault(gid, {}).setdefault(NAME_MODULE, {})['engine'] = msg
	await cfgmgr.save(config)

	await bot.send(ev, f"影之诗查卡器引擎变更为 {msg}", at_sender=True)

def get_group_image_res(gid: str, name: str='') -> Type[R.ResImg]:
	image_dir = os.path.join('shadowverse', 'games', 'images')
	image_path = os.path.join(image_dir, f"{gid}_{name}.png")
	image_res = R.img(image_path)
	os.makedirs(R.img(image_dir).path, exist_ok=True)
	return image_res

@sv.on_fullmatch(('sv猜卡牌解锁', 'sv猜卡牌重启', ))
async def sv_card_guess_unlock(bot, ev: CQEvent):
	gmmgr.finish(ev.group_id)
	await bot.send(ev, '游戏已解锁')

@sv.on_prefix(('sv猜卡牌', ))
async def sv_card_guess(bot, ev: CQEvent):
	if not gmmgr.is_idle(ev.group_id):
		await bot.finish(ev, '游戏仍在进行中…')

	gmmgr.start(ev.group_id)

	msg = ev.message.extract_plain_text()
	gid = str(ev.group_id)

	filters = list(filter(lambda x: x != '', msg.split(' ')))
	sv.logger.debug(f"filters: {filters}")

	config = await cfgmgr.load({})
	config = config.get(gid, {}).get(NAME_MODULE, {})
	set_default_config(config)

	eg = engine.get_engine(config['engine'])

	try:
		cards = await eg.search_std_cards(filters)

		await bot.send(ev, f"使用引擎 {config['engine']} 进行查找\n将在{len(cards)}张卡牌中抽选", at_sender=False)

		if len(cards) == 0:
			gmmgr.finish(ev.group_id)
			await bot.finish(ev, '无卡牌资源')

		card = await eg.get_random_std_card(cards)

		sv.logger.info(f"choose card {card['names']}")
		sv.logger.debug(f"card image: {card['image']}")

		card_image = await eg.get_std_card_image(card)
		card_image_crop = eg.get_std_card_image_crop(card_image)
	except NotImplementedError as e:
		sv.logger.critical(f"{e}")
		gmmgr.finish(ev.group_id)
		await bot.finish(ev, '该引擎此功能未实现')
	except Exception as e:
		sv.logger.critical(f"{e}")
		gmmgr.finish(ev.group_id)
		await bot.finish(ev, '获取卡牌资源出错…')

	img_res = get_group_image_res(gid, f"{NAME_MODULE}_origin")
	card_image.save(img_res.path)

	answer = {
		'names': card['names'],
		'pattern': eg.get_std_card_names_pattern(card),
		'img_res': img_res,
	}

	gmmgr.set_data(ev.group_id, answer)

	card_image_crop = MessageSegment.image(util.pic2b64(card_image_crop))
	try:
		await bot.send(ev, f"猜猜这个图片是哪张卡牌的一部分?({config['time_limit']}s后公布答案) {card_image_crop}")
	except Exception as e:
		sv.logger.critical(f"{e}")
		gmmgr.finish(ev.group_id)
		await bot.finish(ev, '发送失败，已结束')

	await asyncio.sleep(config['time_limit'])

	try:
		if gmmgr.get_winner(ev.group_id) == 0:
			# reach time limit
			gmmgr.win(ev.group_id, -1)
			names = '\n'.join(card['names'])
			await bot.send(ev, f"正确答案是：\n{names} {img_res.cqcode}\n很遗憾，没有人答对~")
		else:
			await bot.send(ev, '本轮猜卡牌游戏结束~')
	except Exception as e:
		sv.logger.critical(f"{e}")

	gmmgr.finish(ev.group_id)

@sv.on_message()
async def sv_card_guess_check(bot, ev: CQEvent):
	if gmmgr.is_idle(ev.group_id) or gmmgr.get_winner(ev.group_id) != 0:
		return

	gid = str(ev.group_id)
	msg = ev.message.extract_plain_text()

	answer = gmmgr.get_data(ev.group_id)

	if answer['pattern'].match(msg):
		gmmgr.win(ev.group_id, ev.user_id)

		sv.logger.info(f"gid {ev.group_id} uid {ev.user_id} bingo~")

		names = '\n'.join(answer['names'])
		await bot.send(ev, f"正确答案是：\n{names} {answer['img_res'].cqcode}\n{MessageSegment.at(ev.user_id)}猜对了，真厉害！\n(此轮游戏将在到达时限后自动结束，请耐心等待)")

