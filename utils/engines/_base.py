#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Union, Tuple, List, Dict, TypedDict, NoReturn

import abc
import re
import copy
import random
import datetime
import asyncio
import aiohttp
import aiocache
import io
import PIL
import PIL.ImageFont
import PIL.ImageDraw
import itertools

from .. import resource
from hoshino import log, config

class TypeStdCard(TypedDict):
	id:             str
	names:          List[str]
	faction:        str
	types:          List[str]
	series:         str
	rarity:         str
	descs:          List[str]
	rules:          List[str]
	attributes:     Tuple[int, int, int]
	image:          str
	evo_descs:      List[str]
	evo_rules:      List[str]
	evo_attributes: Tuple[int, int, int]
	evo_image:      str

class TypeStdCardVoice(TypedDict):
	action: str
	voice:  str

TypeStdCardVoices = List[TypeStdCardVoice]

class TypeImageCropConfig(TypedDict):
	left:   float
	top:    float
	right:  float
	bottom: float
	wsize:  float

class TypeImagesInfoConfig(TypedDict):
	font:          str
	font_size:     int
	font_spacing:  int
	count_max:     int
	line_size_max: int
	card_margin:   int

class BaseEngine():

	_logger_name = f"{'.'.join(__name__.split('.')[2:])}@{__qualname__}"
	_logger = log.new_logger(_logger_name, config.DEBUG)

	@abc.abstractclassmethod
	async def _fetch_data(cls) -> Any:
		raise NotImplementedError

	@classmethod
	@aiocache.cached(ttl=86400)
	async def _get_std_data(cls) -> List[TypeStdCard]:
		return cls.to_std_cards(await cls._fetch_data())

	# code -----------------------------

	@classmethod
	def get_rarity_code(cls, rarity: str) -> int:
		rarity = rarity.lower().rstrip('卡')
		if rarity in [
			'bronze', 'ブロンズレア', 'ブロンズ', '青铜', '青銅', '铜', '銅',
		]:
			return 0
		if rarity in [
			'silver', 'シルバーレア', 'シルバー', '白银', '白銀', '银', '銀',
		]:
			return 1
		if rarity in [
			'gold', 'ゴールドレア', 'ゴールド', '黄金', '金',
		]:
			return 2
		if rarity in [
			'legendary', 'レジェンド', '传说', '傳說', '虹',
		]:
			return 3
		# cls._logger.error(f"unknow rarity: {rarity}")
		return -1

	@classmethod
	def get_faction_code(cls, faction: str) -> int:
		faction = faction.lower()
		if faction in [
			'neutral', 'ニュートラル', '中立',
		]:
			return 0
		if faction in [
			'forestcraft', 'エルフ', '精灵', '精靈', '妖精', '妖',
		]:
			return 1
		if faction in [
			'swordcraft', 'ロイヤル', '皇家护卫', '皇家護衛', '皇室护卫', '皇家', '皇室', '皇',
		]:
			return 2
		if faction in [
			'runecraft', 'ウィッチ', '法师', '法', '巫师', '巫師',
		]:
			return 3
		if faction in [
			'dragoncraft', 'ドラゴン', '龙族', '龍族', '龙', '龍',
		]:
			return 4
		if faction in [
			'shadowcraft', 'ネクロマンサー', '死灵法师', '死靈法師', '死灵术士', '死灵', '死', '唤灵师',
		]:
			return 5
		if faction in [
			'bloodcraft', 'ヴァンパイア', '吸血鬼', '鬼', '血族', '暗夜伯爵',
		]:
			return 6
		if faction in [
			'havencraft', 'ビショップ', '主教', '教',
		]:
			return 7
		if faction in [
			'portalcraft', 'ネメシス', '复仇者', '復仇者', '超越者', '鱼',
		]:
			return 8
		# cls._logger.error(f"unknow faction: {faction}")
		return -1

	@classmethod
	def get_type_code(cls, type: str) -> int:
		if type in [
			'followers', 'follower', 'フォロワー', '从者', '随从',
		]:
			return 0
		if type in [
			'spells', 'spell', 'スペル', '法术',
		]:
			return 1
		if type in [
			'amulets', 'amulet', 'アミュレット', '护符', '魔法阵',
		]:
			return 2
		# cls._logger.error(f"unknow type: {type}")
		return -1

	@classmethod
	def get_series_code(cls, series: str) -> int:
		raise NotImplementedError

	@staticmethod
	def check_code_equal(a: int, b: int) -> bool:
		return (a >= 0) and (b >= 0) and (a == b)

	# cast -----------------------------

	@abc.abstractclassmethod
	def to_std_card(cls, card: Any) -> TypeStdCard:
		raise NotImplementedError

	@abc.abstractclassmethod
	def to_std_cards(cls, cards: Any) -> List[TypeStdCard]:
		raise NotImplementedError

	# data -----------------------------

	@classmethod
	async def get_all_std_cards(cls) -> List[TypeStdCard]:
		return copy.deepcopy(await cls._get_std_data())

	@classmethod
	async def get_random_std_card(cls, cards: List[TypeStdCard]=None) -> TypeStdCard:
		if cards == None:
			return copy.deepcopy(random.choice(await cls._get_std_data()))
		else:
			return copy.deepcopy(random.choice(cards))

	@classmethod
	async def get_random_std_cards(cls, n: int, cards: List[TypeStdCard]=None) -> List[TypeStdCard]:
		if cards == None:
			return copy.deepcopy(random.sample(await cls._get_std_data(), n))
		else:
			return copy.deepcopy(random.sample(cards, n))

	# search ---------------------------

	@classmethod
	async def get_std_card_by_id(cls, id: str) -> TypeStdCard:
		for card in await cls.get_all_std_cards():
			if card.get('id') == id:
				return card

	PUNCTUATION = (
		# Chinese
		'\uFF02\uFF03\uFF04\uFF05\uFF06\uFF07\uFF08\uFF09\uFF0A\uFF0B\uFF0C\uFF0D'
		'\uFF0F\uFF1A\uFF1B\uFF1C\uFF1D\uFF1E\uFF20\uFF3B\uFF3C\uFF3D\uFF3E\uFF3F'
		'\uFF40\uFF5B\uFF5C\uFF5D\uFF5E\uFF5F\uFF60'
		'\uFF62\uFF63\uFF64'
		'\u3000\u3001\u3003'
		'\u3008\u3009\u300A\u300B\u300C\u300D\u300E\u300F\u3010\u3011'
		'\u3014\u3015\u3016\u3017\u3018\u3019\u301A\u301B\u301C\u301D\u301E\u301F'
		'\u3030'
		'\u303E\u303F'
		'\u2013\u2014'
		'\u2018\u2019\u201B\u201C\u201D\u201E\u201F'
		'\u2026\u2027'
		'\uFE4F'
		'\uFE51\uFE54'
		'\u00B7'
		'\uFF01'
		'\uFF1F'
		'\uFF61'
		'\u3002'
	) + (
		# Japanese
		'\u30fb'
	) + (
		# English
		'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
	)
	IGNORED_CHARS_IN_NAME = PUNCTUATION + (
		'　的'
		' '
		'áéö'
		'★'
	)

	@classmethod
	def get_std_card_names_pattern(cls, card: TypeStdCard) -> re.Pattern:
		patterns = [
			''.join(map(
				lambda x: '.?' if x in cls.IGNORED_CHARS_IN_NAME else x,
				name.strip()
			)) for name in card['names']
		]
		return re.compile('|'.join(patterns), flags=re.IGNORECASE)

	@classmethod
	def filter_std_cards(cls, cards: List[TypeStdCard], f: str) -> List[TypeStdCard]:
		cls._logger.debug(f"filter \"{f}\" in {len(cards)} cards")
		if f == '':
			return copy.deepcopy(cards)
		result = []
		cost_match = re.match(r'^(\d+)(?:00|费)$', f)
		if cost_match:
			cost = int(cost_match.group(1))
			result = list(filter(
				lambda card: card.get('attributes', (-1))[0] == cost,
				cards
			))
		elif re.match(r'^\d+$', f):
			result = list(filter(
				lambda card: ''.join(map(str, card.get('attributes', ()))) == f,
				cards
			))
		else:
			for card in cards:
				if (any(map(lambda x: f in x, card.get('names', []))) or
					any(map(lambda x: f in x, card.get('rules', []))) or
					any(map(lambda x: f in x, card.get('types', []))) or
					cls.check_code_equal(
						cls.get_type_code(card.get('types')[0]),
						cls.get_type_code(f)
					) or
					card.get('faction') == f or
					cls.check_code_equal(
						cls.get_faction_code(card.get('faction')),
						cls.get_faction_code(f)
					) or
					card.get('series') == f or
					card.get('rarity') == f or
					cls.check_code_equal(
						cls.get_rarity_code(card.get('rarity')),
						cls.get_rarity_code(f)
					)):
					result.append(card)
		cls._logger.debug(f"find {len(result)} cards")
		# return copy.deepcopy(result)
		return result

	@classmethod
	async def search_std_cards(cls, filters: List[str]) -> List[TypeStdCard]:
		cards = await cls._get_std_data()
		for f in filters:
			cards = cls.filter_std_cards(cards, f)
		return copy.deepcopy(cards)

	# net ------------------------------

	DEFAULT_HEADERS = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
	}

	@classmethod
	async def _get_url_data(cls, url: str, **kwargs) -> bytes:
		cls._logger.info(f"GET data: {url}")
		kwargs.setdefault('headers', __class__.DEFAULT_HEADERS)
		async with aiohttp.ClientSession() as session:
			try:
				async with session.get(url, **kwargs) as response:
					ret = await response.read()
			except Exception as e:
				cls._logger.error(f"{e}")
				cls._logger.error(f"GET data: {url} failed")
				raise
		cls._logger.info(f"GET data: {url} succeed")
		return ret

	@classmethod
	async def _get_url_text(cls, url: str, **kwargs) -> str:
		cls._logger.info(f"GET text: {url}")
		kwargs.setdefault('headers', __class__.DEFAULT_HEADERS)
		async with aiohttp.ClientSession() as session:
			try:
				async with session.get(url, **kwargs) as response:
					ret = await response.text()
			except Exception as e:
				cls._logger.error(f"{e}")
				cls._logger.error(f"GET text: {url} failed")
				raise
		cls._logger.info(f"GET text: {url} succeed")
		return ret

	@classmethod
	async def _get_url_json(cls, url: str, **kwargs) -> Union[List, Dict]:
		cls._logger.info(f"GET json: {url}")
		kwargs.setdefault('headers', __class__.DEFAULT_HEADERS)
		async with aiohttp.ClientSession() as session:
			try:
				async with session.get(url, **kwargs) as response:
					ret = await response.json(content_type=None)
			except Exception as e:
				cls._logger.error(f"{e}")
				cls._logger.error(f"GET json: {url} failed")
				raise
		cls._logger.info(f"GET json: {url} succeed")
		return ret

	@classmethod
	async def _post_url_data(cls, url: str, **kwargs) -> bytes:
		cls._logger.info(f"POST data: {url}")
		kwargs.setdefault('headers', __class__.DEFAULT_HEADERS)
		async with aiohttp.ClientSession() as session:
			try:
				async with session.post(url, **kwargs) as response:
					ret = await response.read()
			except Exception as e:
				cls._logger.error(f"{e}")
				cls._logger.error(f"POST data: {url} failed")
				raise
		cls._logger.info(f"POST data: {url} succeed")
		return ret

	@classmethod
	async def _post_url_text(cls, url: str, **kwargs) -> str:
		cls._logger.info(f"POST text: {url}")
		kwargs.setdefault('headers', __class__.DEFAULT_HEADERS)
		async with aiohttp.ClientSession() as session:
			try:
				async with session.post(url, **kwargs) as response:
					ret = await response.text()
			except Exception as e:
				cls._logger.error(f"{e}")
				cls._logger.error(f"POST text: {url} failed")
				raise
		cls._logger.info(f"POST text: {url} succeed")
		return ret

	@classmethod
	async def _post_url_json(cls, url: str, **kwargs) -> Union[List, Dict]:
		cls._logger.info(f"POST json: {url}")
		kwargs.setdefault('headers', __class__.DEFAULT_HEADERS)
		async with aiohttp.ClientSession() as session:
			try:
				async with session.post(url, **kwargs) as response:
					ret = await response.json(content_type=None)
			except Exception as e:
				cls._logger.error(f"{e}")
				cls._logger.error(f"POST json: {url} failed")
				raise
		cls._logger.info(f"POST json: {url} succeed")
		return ret

	@classmethod
	async def _get_urls_data(cls, urls: List[str], **kwargs) -> List[Union[bytes, type(None)]]:
		# cls._logger.info(f"get urls: [{len(urls)}]")
		cls._logger.info(f"GET data: {urls}")
		kwargs.setdefault('headers', __class__.DEFAULT_HEADERS)
		async def fetch(session: aiohttp.client.ClientSession, url: str) -> bytes:
			try:
				async with session.get(url, **kwargs) as response:
					return await response.read()
			except Exception as e:
				cls._logger.error(f"{e}")
				cls._logger.error(f"GET data: {url} failed")
				return None
		async with aiohttp.ClientSession() as session:
			ret = await asyncio.gather(
				*[fetch(session, url) for url in urls]
			)
		cls._logger.info(f"GET data: [{len(urls)-ret.count(None)}] succeed")
		return ret

	@classmethod
	async def _get_urls_text(cls, urls: List[str], **kwargs) -> List[Union[str, type(None)]]:
		# cls._logger.info(f"get urls: [{len(urls)}]")
		cls._logger.info(f"GET text: {urls}")
		kwargs.setdefault('headers', __class__.DEFAULT_HEADERS)
		async def fetch(session: aiohttp.client.ClientSession, url: str) -> bytes:
			try:
				async with session.get(url, **kwargs) as response:
					return await response.text()
			except Exception as e:
				cls._logger.error(f"{e}")
				cls._logger.error(f"GET text: {url} failed")
				return None
		async with aiohttp.ClientSession() as session:
			ret = await asyncio.gather(
				*[fetch(session, url) for url in urls]
			)
		cls._logger.info(f"GET text: [{len(urls)-ret.count(None)}] succeed")
		return ret

	@classmethod
	async def _get_urls_json(cls, urls: List[str], **kwargs) -> List[Union[List, Dict, type(None)]]:
		# cls._logger.info(f"get urls: [{len(urls)}]")
		cls._logger.info(f"GET json: {urls}")
		kwargs.setdefault('headers', __class__.DEFAULT_HEADERS)
		async def fetch(session: aiohttp.client.ClientSession, url: str) -> bytes:
			try:
				async with session.get(url, **kwargs) as response:
					return await response.json(content_type=None)
			except Exception as e:
				cls._logger.error(f"{e}")
				cls._logger.error(f"GET json: {url} failed")
				return None
		async with aiohttp.ClientSession() as session:
			ret = await asyncio.gather(
				*[fetch(session, url) for url in urls]
			)
		cls._logger.info(f"GET json: [{len(urls)-ret.count(None)}] succeed")
		return ret

	# image ----------------------------

	@classmethod
	async def get_std_card_image(cls, card: TypeStdCard) -> PIL.Image.Image:
		bytes = io.BytesIO(await cls._get_url_data(card['image']))
		image = PIL.Image.open(bytes).convert("RGBA")
		return image

	@classmethod
	async def get_std_card_images(cls, cards: List[TypeStdCard]) -> List[PIL.Image.Image]:
		images = [
			PIL.Image.open(io.BytesIO(bytes)).convert("RGBA") if bytes else \
				PIL.Image.open(io.BytesIO(resource.images['error.png'])).convert("RGBA") \
				for bytes in await cls._get_urls_data([card['image'] for card in cards])
		]
		return images

	# can override
	DEFAULT_IMAGE_CROP_CONFIG = {
		'left':   0.138,
		'top':    0.185,
		'right':  0.860,
		'bottom': 0.860,
		'wsize':  0.20,
	}

	@classmethod
	def get_std_card_image_crop(cls, image: PIL.Image.Image, config: TypeImageCropConfig=None) -> PIL.Image.Image:
		if config == None:
			config = cls.DEFAULT_IMAGE_CROP_CONFIG
		x0 = int(image.size[0] * config['left'])
		y0 = int(image.size[1] * config['top'])
		ws = int(image.size[1] * config['wsize'])
		x1 = int(image.size[0] * config['right']) - ws
		y1 = int(image.size[1] * config['bottom']) - ws
		x2 = random.randint(x0, x1)
		y2 = random.randint(y0, y1)
		return image.crop((x2, y2, x2 + ws, y2 + ws))

	@staticmethod
	def _get_multiline_textsize(lines: List[str], font: PIL.ImageFont.FreeTypeFont, spacing: int=4) -> Tuple[int, int]:
		sizes = [font.getsize(line) for line in lines]
		return (max(sizes)[0], sum(list(zip(*sizes))[1])+spacing*(len(sizes)-1))

	@staticmethod
	def _make_text_lines(card: TypeStdCard, line_size_max: int=40) -> List[str]:

		def utf8_size(text: str) -> int:
			return int((len(text.encode('UTF-8'))-len(text))/2+len(text))

		def cut(text: str, line_size_max: int) -> List[str]:
			SEPEND = r'[；，。！」]'
			SEP = [
				' ', '，', '、', '；', '—', '……',
				f'。(?!{SEPEND})', f'！(?!{SEPEND})',
				'(?<!^)(?=（)', f'）(?!{SEPEND})',
				'(?<!^)(?=「)', f'」(?!{SEPEND})',
				# '(?<=<br>)',
			]
			result = []
			size = utf8_size(text)
			while size > line_size_max:
				seps = list(itertools.chain.from_iterable(map(
					lambda x: [i.end() for i in re.finditer(x, text)],
					SEP
				))) + [len(text)]
				# assert all([i > 0 for i in seps])
				fragment = min([(abs(utf8_size(text[:i])-line_size_max), i) for i in seps])
				result.append(text[:fragment[1]])
				text = text[fragment[1]:]
				size = utf8_size(text)
			if text:
				result.append(text)
			return result

		result = []
		result.extend(card['names'])
		result.append(' ')
		result.append(card['series'])
		result.append(' ')
		result.append('/'.join([card['faction']]+card['types']))
		result.append('-' * line_size_max)
		result.append(f"{card['attributes']}")
		result.append(' ')
		for text in card['descs']:
			for line in text.split('\n'):
				result.extend(cut(line, line_size_max))
		result.append(' ')
		for text in card['rules']:
			for line in text.split('\n'):
				result.extend(cut(line, line_size_max))
		result.append('-' * line_size_max)
		result.append(f"{card['evo_attributes']}")
		result.append(' ')
		for text in card['evo_descs']:
			for line in text.split('\n'):
				result.extend(cut(line, line_size_max))
		result.append(' ')
		for text in card['evo_rules']:
			for line in text.split('\n'):
				result.extend(cut(line, line_size_max))
		return result

	@classmethod
	async def generate_std_cards_info_image(cls, cards: List[TypeStdCard], config: TypeImagesInfoConfig) -> PIL.Image.Image:

		cards = cards[:config['count_max']]
		font = PIL.ImageFont.truetype(
			font=config['font'],
			size=config['font_size'],
			index=0,
			encoding='unic',
			layout_engine=None
		)

		card_images = await cls.get_std_card_images(cards)
		card_width_min = min(map(lambda x: x.size[0], card_images))

		text_sections = []
		text_sizes = []

		for card in cards:
			text_lines = cls._make_text_lines(card, config['line_size_max'])
			text_size = cls._get_multiline_textsize(text_lines, font, config['font_spacing'])
			text_sections.append(text_lines)
			text_sizes.append(text_size)

		for card_image in card_images:
			card_image = card_image.thumbnail((card_width_min, card_image.size[1]), PIL.Image.ANTIALIAS)

		card_width_max = card_width_min
		card_margin = config['card_margin']

		image_size = (
			max(map(
				lambda i: card_images[i].size[0] + text_sizes[i][0],
				range(len(cards))
			)) + card_margin * 3,
			sum(map(
				lambda i: max(card_images[i].size[1], text_sizes[i][1]),
				range(len(cards))
			)) + card_margin * (len(cards) + 1)
		)

		image = PIL.Image.new(mode='RGBA', size=image_size, color='white')
		draw = PIL.ImageDraw.Draw(image)

		section_top = card_margin
		for i in range(len(cards)):
			section_height = max(card_images[i].size[1], text_sizes[i][1])
			image.paste(
				im=card_images[i],
				box=(
					int((card_width_max-card_images[i].size[0])/2) + card_margin,
					int((section_height-card_images[i].size[1])/2) + section_top,
				),
				mask=card_images[i]
			)
			text_size = text_sizes[i]
			top = section_top + int((section_height-text_size[1])/2)
			left = card_width_max + card_margin * 2
			text_lines = text_sections[i]
			for text_line in text_lines:
				line_size = font.getsize(text_line)
				draw.text(
					xy=(left, top),
					text=text_line,
					fill='black',
					font=font,
					anchor='la',
					spacing=0,
					align='left',
					# direction=None,
					# features=None,
					# language=None,
					stroke_width=0,
					stroke_fill=None,
					embedded_color=False
				)
				top += line_size[1] + config['font_spacing']
			section_top += section_height + card_margin

		any(map(lambda x: x.close(), card_images))

		return image

	# voice ----------------------------

	@abc.abstractclassmethod
	async def get_std_card_voices(cls, card: TypeStdCard) -> TypeStdCardVoices:
		raise NotImplementedError

	@classmethod
	async def get_std_card_voice(cls, voice: TypeStdCardVoice) -> bytes:
		return await cls._get_url_data(voice['voice'])
