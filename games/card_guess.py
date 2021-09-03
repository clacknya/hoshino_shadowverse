#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Type, Union, Dict, NoReturn

from hoshino import Service, R, util
from hoshino.typing import CQEvent, MessageSegment

import os
import io
import json
import asyncio
import aiofiles
import aiorwlock

from .. import _engines as engines
from . import utils

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_CONFIG = os.path.join(PATH_ROOT, 'config.json')

VAR_DATA = {}

LOCK_CONFIG = aiorwlock.RWLock()
LOCK_PLAYERS = aiorwlock.RWLock()

sv = Service('影之诗猜卡牌', bundle='sv娱乐', help_='''
[sv猜卡牌] 进行猜卡牌游戏
[sv猜卡牌重启] 当猜卡牌游戏死锁时解锁
'''.strip())

def set_default_config(config: Dict={}) -> Dict:
	config.setdefault('engine', 'iyingdi')
	card_guess = config.setdefault('card_guess', {})
	card_guess.setdefault('left', 0.138)
	card_guess.setdefault('top', 0.185)
	card_guess.setdefault('right', 0.860)
	card_guess.setdefault('bottom', 0.860)
	card_guess.setdefault('wsize', 0.20)
	card_guess.setdefault('patch_size', 64)
	card_guess.setdefault('time_limit', 30)
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

async def get_data(gid: str) -> Union[None, Dict]:
	async with LOCK_PLAYERS.reader_lock:
		result = VAR_DATA.get(gid)
		if isinstance(result, dict):
			result = result.copy()
	return result

async def set_data(gid: str, data: Union[None, Dict]) -> NoReturn:
	async with LOCK_PLAYERS.writer_lock:
		if isinstance(data, dict):
			data = data.copy()
		VAR_DATA[gid] = data

def get_group_image_res(gid: str, name: str='') -> Type[R.ResImg]:
	images_path = os.path.join('shadowverse', 'games', 'images')
	images_res = R.img(images_path)
	if not os.path.isdir(images_res.path):
		os.makedirs(images_res.path)
	image_path = os.path.join(images_path, f"{gid}_{name}.png")
	image_res = R.img(image_path)
	return image_res

@sv.on_fullmatch(('sv_card_guess_reset', 'sv猜卡牌重启'))
async def sv_card_guess_reset(bot, ev: CQEvent):
	gid = str(ev.group_id)
	await set_data(gid, None)
	await bot.send(ev, '游戏已重启')

@sv.on_fullmatch(('sv_card_guess', 'sv猜卡牌'))
async def sv_card_guess(bot, ev: CQEvent):
	gid = str(ev.group_id)

	if not isinstance(await get_data(gid), type(None)):
		await bot.finish(ev, '游戏仍在进行中…')

	await set_data(gid, {})

	config = await load_config()
	config = config.get(gid, {})
	set_default_config(config)

	e = engines.get_engine(config['engine'])
	cards = await e.cards_all()

	card_guess = config['card_guess']

	card = utils.get_random_card(cards, card_guess)

	sv.logger.info(f"choose card {card['names']}")
	sv.logger.debug(f"card image: {card['image']}")

	card_image = await utils.get_card_image(card, card_guess)
	card_image_crop = utils.crop_card_image(card_image, card_guess)

	answer = {
		'names': card['names'],
		'pattern': utils.get_name_match_pattern(card),
		'image': card_image,
	}

	await set_data(gid, answer)

	card_image_crop = MessageSegment.image(util.pic2b64(card_image_crop))
	await bot.send(ev, f"猜猜这个图片是哪张卡牌的一部分?({card_guess['time_limit']}s后公布答案) {card_image_crop}")
	await asyncio.sleep(card_guess['time_limit'])

	result = await get_data(gid)
	await set_data(gid, None)

	if not result.get('winner'):
		names = '\n'.join(card['names'])
		img_res = get_group_image_res(gid, 'origin')
		card_image.save(img_res.path)
		await bot.send(ev, f"正确答案是：\n{names} {img_res.cqcode}\n很遗憾，没有人答对~")

@sv.on_message()
async def sv_card_guess_check(bot, ev: CQEvent):
	gid = str(ev.group_id)

	data = await get_data(gid)
	if not data or data.get('winner'):
		return

	msg = ev.message.extract_plain_text()
	if data['pattern'].match(msg):
		data['winner'] = ev.user_id
		await set_data(gid, data)

		sv.logger.info(f"uid {ev.user_id} bingo~")

		names = '\n'.join(data['names'])
		img_res = get_group_image_res(gid, 'origin')
		data['image'].save(img_res.path)
		await bot.send(ev, f"正确答案是：\n{names} {img_res.cqcode}\n{MessageSegment.at(ev.user_id)}猜对了，真厉害！\n(此轮游戏将在到达时限后自动结束，请耐心等待)")

