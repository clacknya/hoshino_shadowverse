#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Type, Union, Dict, NoReturn

from hoshino import Service, R, util
from hoshino.typing import CQEvent, MessageSegment

import os
import random
import asyncio
import aiofiles

from ..utils import engine
from ..utils import manager
from .init import cfgmgr

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))

NAME_MODULE = __name__.split('.')[-1]

gmmgr = manager.GameManager(NAME_MODULE)

sv = Service('影之诗猜语音', bundle='sv娱乐', help_='''
[sv猜语音 关键词 关键词 ...] 进行猜语音游戏，可选关键词筛选
[sv猜语音引擎列表] 列出可用查询引擎
[sv猜语音引擎设定 名称] 设定查询引擎
'''.strip())
# [sv猜语音解锁] 当猜语音游戏超时限未自动结束死锁时解锁

def set_default_config(config: Dict={}) -> Dict:
	config.setdefault('engine', 'svgdb_jp')
	config.setdefault('time_limit', 30)
	return config

@sv.on_fullmatch(('sv猜语音引擎列表', ))
async def sv_voice_guess_engine_list(bot, ev: CQEvent):
	await bot.send(ev, '列表：\n' + '\n'.join([f"引擎: {name}, 源: {source}" for name, source in engine.list_engines()]), at_sender=True)

@sv.on_prefix(('sv猜语音引擎设定', ))
async def sv_voice_guess_engine_set(bot, ev: CQEvent):
	msg = ev.message.extract_plain_text()
	gid = str(ev.group_id)

	if msg not in engine.get_engines():
		await bot.send(ev, f"引擎 {msg} 不存在", at_sender=True)
		return

	config = await cfgmgr.load({})
	config.setdefault(gid, {}).setdefault(NAME_MODULE, {})['engine'] = msg
	await cfgmgr.save(config)

	await bot.send(ev, f"影之诗猜语音引擎变更为 {msg}", at_sender=True)

def get_group_voice_res(gid: str, name: str='') -> Type[None]:
	voice_dir = os.path.join('shadowverse', 'games', 'voices')
	os.makedirs(R.get(voice_dir).path, exist_ok=True)
	return R.get(voice_dir, f"{gid}_{name}.voice")

@sv.on_fullmatch(('sv猜语音解锁', 'sv猜语音重启', ))
async def sv_voice_guess_unlock(bot, ev: CQEvent):
	gmmgr.finish(ev.group_id)
	await bot.send(ev, '游戏已解锁')

@sv.on_prefix(('sv猜语音', ))
async def sv_voice_guess(bot, ev: CQEvent):
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

	if eg == None:
		sv.logger.critical(f"未找到引擎 {config['engine']}")
		gmmgr.finish(ev.group_id)
		await bot.finish(ev, f"未找到引擎 {config['engine']}")

	try:
		cards = await eg.search_std_cards(filters)

		await bot.send(ev, f"使用引擎 {config['engine']} 进行查找\n将在{len(cards)}张卡牌中抽选", at_sender=False)

		if len(cards) == 0:
			gmmgr.finish(ev.group_id)
			await bot.send(ev, '无卡牌资源')
			return

		card = await eg.get_random_std_card(cards)

		sv.logger.info(f"choose card id: {card['id']}, name: {card['names']}")

		voices = await eg.get_std_card_voices(card)

		if len(voices) == 0:
			gmmgr.finish(ev.group_id)
			await bot.send(ev, f"此卡牌 {card['names']} 无语音，自动结束")
			return
		else:
			sv.logger.info(f"find {len(voices)} voices")

		voice = random.choice(voices)
		voice_content = await eg.get_std_card_voice(voice)
	except NotImplementedError as e:
		sv.logger.critical('NotImplementedError')
		gmmgr.finish(ev.group_id)
		await bot.finish(ev, '该引擎此功能未实现')
	except Exception as e:
		sv.logger.critical(f"{e}")
		gmmgr.finish(ev.group_id)
		await bot.finish(ev, '获取语音资源出错…')

	vo_res = get_group_voice_res(gid, NAME_MODULE)

	async with aiofiles.open(vo_res.path, 'wb') as f:
		await f.write(voice_content)

	answer = {
		'names': card['names'],
		'pattern': eg.get_std_card_names_pattern(card),
		'vo_res': vo_res,
	}

	gmmgr.set_data(ev.group_id, answer)

	rec = MessageSegment.record(f'file:///{os.path.abspath(vo_res.path)}')

	try:
		await bot.send(ev, rec)
		await bot.send(ev, f"猜猜这个语音是哪张卡牌的({voice['action']})?({config['time_limit']}s后公布答案)")
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
			await bot.send(ev, f"正确答案是：\n{names}\n很遗憾，没有人答对~")
		else:
			await bot.send(ev, '本轮猜语音游戏结束~')
	except Exception as e:
		sv.logger.critical(f"{e}")

	gmmgr.finish(ev.group_id)

@sv.on_message()
async def sv_voice_guess_check(bot, ev: CQEvent):
	if (gmmgr.is_idle(ev.group_id) or not gmmgr.is_data_set(ev.group_id) or
		gmmgr.get_winner(ev.group_id) != 0):
		return

	answer = gmmgr.get_data(ev.group_id)

	gid = str(ev.group_id)
	msg = ev.message.extract_plain_text()

	if answer['pattern'].match(msg):
		gmmgr.win(ev.group_id, ev.user_id)

		sv.logger.info(f"gid {ev.group_id} uid {ev.user_id} bingo~")

		names = '\n'.join(answer['names'])
		await bot.send(ev, f"正确答案是：\n{names}\n{MessageSegment.at(ev.user_id)}猜对了，真厉害！\n(此轮游戏将在到达时限后自动结束，请耐心等待)")
