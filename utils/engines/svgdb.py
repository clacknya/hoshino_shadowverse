#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, TypedDict

import asyncio
import datetime

from . import _base as base
from . import _svgdb
from hoshino import log, config

class svgdb_en(_svgdb.svgdb):

	URL = 'https://svgdb.me/api/en'
	SOURCE = 'svgdb EN'

	_logger_name = f"{'.'.join(__name__.split('.')[2:])}@{__qualname__}"
	_logger = log.new_logger(_logger_name, config.DEBUG)

	_translation = {
		'cards': 'Cards',
		'leaders': 'Leaders',
		'sleeves': 'Sleeves',
		'cardSearch': 'Search Cards',
		'follower': 'Follower',
		'amulet': 'Amulet',
		'japanese': 'Japanese',
		'english': 'English',
		'baseFlair': 'Base Flair',
		'evolvedFlair': 'Evolved Flair',
		'play': 'Play',
		'attack': 'Attack',
		'evolve': 'Evolve',
		'death': 'Death',
		'tournaments': 'Tournaments',
		'rotation': 'Rotation',
		'unlimited': 'Unlimited',
		'relatedCards': 'Related Cards',
		'type': 'Type',
		'rarity': 'Rarity',
		'set': 'Set',
		'cost': 'Cost',
		'base': 'Base',
		'evolved': 'Evolved',
		'stats': 'Stats',
		'effect': 'Effect: ',
		'accelerate': 'Accelerate',
		'crystallize': 'Crystallize',
		'unionBurst': 'Union Burst',
		'enhance': 'Enhance',
		'effectSpecial': 'Effect/Special',
		'art': 'Art',
		'hideAltArt': 'Hide Alt Art',
		'showAltArt': 'Show Alt Art',
		'deckbuilder': 'Deckbuilder',
		'effectVoice': 'Effect',
		'resources': 'Resources',
		'backgrounds': 'Backgrounds',
		'emblems': 'Emblems',
		'flairs': 'Flairs',
		'censored': 'Censored',
		'animated': 'Animated'
	}

	@classmethod
	def _parse_trait(cls, trait: str) -> List[str]:
		return trait.split(' / ')

	@classmethod
	def _get_image_url_by_id(cls, id: str) -> str:
		return f"https://svgdb.me/assets/cards/en/C_{id}.png"

	@classmethod
	def _get_evo_image_url_by_id(cls, id: str) -> str:
		return f"https://svgdb.me/assets/cards/en/E_{id}.png"

	@classmethod
	def _get_voice_url_by_file(cls, voice: str) -> str:
		return f"https://svgdb.me/assets/audio/en/{voice}"

class svgdb_jp(_svgdb.svgdb):

	URL = 'https://svgdb.me/api/jp'
	SOURCE = 'svgdb JP'

	_logger_name = f"{'.'.join(__name__.split('.')[2:])}@{__qualname__}"
	_logger = log.new_logger(_logger_name, config.DEBUG)

	_translation = {
		'cards': '\u30ab\u30fc\u30c9',
		'leaders': '\u30ea\u30fc\u30c0\u30fc\u30b9\u30ad\u30f3',
		'sleeves': '\u30b9\u30ea\u30fc\u30d6',
		'cardSearch': '\u30ab\u30fc\u30c9\u691c\u7d22',
		'follower': '\u30d5\u30a9\u30ed\u30ef\u30fc',
		'amulet': '\u30a2\u30df\u30e5\u30ec\u30c3\u30c8',
		'japanese': '\u65e5\u672c\u8a9e',
		'english': '\u82f1\u8a9e',
		'baseFlair': '\u9032\u5316\u524d \u30d5\u30ec\u30fc\u30d0\u30fc\u30c6\u30ad\u30b9\u30c8',
		'evolvedFlair': '\u9032\u5316\u5f8c \u30d5\u30ec\u30fc\u30d0\u30fc\u30c6\u30ad\u30b9\u30c8',
		'play': '\u30d7\u30ec\u30a4',
		'attack': '\u653b\u6483',
		'evolve': '\u9032\u5316',
		'death': '\u6b7b',
		'tournaments': '\u5927\u4f1a',
		'rotation': '\u30ed\u30fc\u30c6',
		'unlimited': '\u30a2\u30f3\u30ea\u30df',
		'relatedCards': '\u95a2\u9023\u30ab\u30fc\u30c9',
		'type': '\u30bf\u30a4\u30d7',
		'rarity': '\u30ec\u30a2\u30ea\u30c6\u30a3',
		'set': '\u30d1\u30c3\u30af',
		'cost': '\u30b3\u30b9\u30c8',
		'base': '\u9032\u5316\u524d',
		'evolved': '\u9032\u5316\u5f8c',
		'stats': '\u653b\u6483\u529b/\u4f53\u529b',
		'effect': '',
		'effectVoice': '\u30a8\u30d5\u30a7\u30af\u30c8',
		'accelerate': '\u30a2\u30af\u30bb\u30e9\u30ec\u30fc\u30c8',
		'crystallize': '\u7d50\u6676',
		'unionBurst': '\u30e6\u30cb\u30aa\u30f3\u30d0\u30fc\u30b9\u30c8',
		'enhance': '\u30a8\u30f3\u30cf\u30f3\u30b9',
		'effectSpecial': '\u30a8\u30d5\u30a7\u30af\u30c8/\u7279\u5225',
		'art': '\u30a4\u30e9\u30b9\u30c8',
		'hideAltArt': 'Alt \u30a4\u30e9\u30b9\u30c8\u975e\u8868\u793a',
		'showAltArt': 'Alt \u30a4\u30e9\u30b9\u30c8\u8868\u793a',
		'Toggle Zoom': '\u30ba\u30fc\u30e0\u30c8\u30b0\u30eb',
		'Toggle Win/Lose': '\u52dd\u5229/\u6557\u5317\u30c8\u30b0\u30eb',
		'Greeting': '\u6328\u62f6',
		'Thanks': '\u611f\u8b1d',
		'Apology': '\u8b1d\u7f6a',
		'Impressed': '\u79f0\u8cdb',
		'Shocked': '\u9a5a\u304d',
		'Thinking': '\u601d\u8003\u4e2d',
		'Taunt': '\u6311\u767a',
		'Start': '\u958b\u59cb',
		'Victory': '\u52dd\u5229',
		'Concede': '\u30ea\u30bf\u30a4\u30a2',
		'Evolve': '\u9032\u5316',
		'Hurt': '\u6bb4\u3089\u308c\u308b\u6642',
		'View Leader Animations': '\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u3092\u898b\u308b',
		'Close': '\u9589\u3058\u308b',
		'Switch animation': '\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u3092\u5909\u3048\u308b',
		'Artist': '\u30a4\u30e9\u30b9\u30c8\u30ec\u30fc\u30bf\u30fc',
		'Switch expression': '\u8868\u60c5\u3092\u5909\u3048\u308b',
		'Deckbuilder': '\u30c7\u30c3\u30ad\u4f5c\u6210',
		'\u30ea\u30ca\u30bb\u30f3\u30c8\u30fb\u30af\u30ed\u30cb\u30af\u30eb': 'Renascent Chronicles',
		'\u6697\u9ed2\u306e\u30a6\u30a7\u30eb\u30b5': 'Darkness Over Vellsar',
		'\u5341\u5929\u899a\u9192': 'Eternal Awakening',
		'\u30ec\u30f4\u30a3\u30fc\u30eb\u306e\u65cb\u98a8': 'Storm Over Rivayle',
		'\u904b\u547d\u306e\u795e\u3005': 'Fortunes Hand',
		'\u30ca\u30c6\u30e9\u5d29\u58ca': 'World Uprooted',
		'\u30a2\u30eb\u30c6\u30a3\u30e1\u30c3\u30c8\u30b3\u30ed\u30b7\u30a2\u30e0': 'Ultimate Colosseum',
		'\u68ee\u7f85\u5486\u54ee': 'Verdant Conflict',
		'\u30ea\u30d0\u30fc\u30b9\u30fb\u30aa\u30d6\u30fb\u30b0\u30ed\u30fc\u30ea\u30fc': 'Rebirth of Glory',
		'\u92fc\u9244\u306e\u53cd\u9006\u8005': 'Steel Rebellion',
		'\u6b21\u5143\u6b6a\u66f2': 'Altersphere',
		'\u5341\u798d\u7d76\u5091': 'Omen of the Ten',
		'\u84bc\u7a7a\u306e\u9a0e\u58eb': 'Brigade of the Sky',
		'\u8d77\u6e90\u306e\u5149\u3001\u7d42\u7109\u306e\u95c7': 'Dawnbreak, Nightedge',
		'\u6642\u7a7a\u8ee2\u751f': 'Chronogenesis',
		'\u661f\u795e\u306e\u4f1d\u8aac': 'Starforged Legends',
		'\u30ef\u30f3\u30c0\u30fc\u30e9\u30f3\u30c9\u30fb\u30c9\u30ea\u30fc\u30e0\u30ba': 'Wonderland Dreams',
		'\u795e\u3005\u306e\u9a12\u5d50': 'Tempest of the Gods',
		'\u30d0\u30cf\u30e0\u30fc\u30c8\u964d\u81e8': 'Rise of Bahamut',
		'\u30c0\u30fc\u30af\u30cd\u30b9\u30fb\u30a8\u30dc\u30eb\u30f4': 'Darkness Evolved',
		'\u30af\u30e9\u30b7\u30c3\u30af': 'Classic',
		'\u30d9\u30fc\u30b7\u30c3\u30af': 'Basic',
		'\u30c8\u30fc\u30af\u30f3': 'Token',
		'Alt': '\u30a4\u30e9\u30b9\u30c8\u9055\u3044',
		'\u30a4\u30e9\u30b9\u30c8\u9055\u3044': 'Alt',
		'Fortunes Hand': '\u904b\u547d\u306e\u795e\u3005',
		'World Uprooted': '\u30ca\u30c6\u30e9\u5d29\u58ca',
		'Ultimate Colosseum': '\u30a2\u30eb\u30c6\u30a3\u30e1\u30c3\u30c8\u30b3\u30ed\u30b7\u30a2\u30e0',
		'Verdant Conflict': '\u68ee\u7f85\u5486\u54ee',
		'Rebirth of Glory': '\u30ea\u30d0\u30fc\u30b9\u30fb\u30aa\u30d6\u30fb\u30b0\u30ed\u30fc\u30ea\u30fc',
		'Steel Rebellion': '\u92fc\u9244\u306e\u53cd\u9006\u8005',
		'Altersphere': '\u6b21\u5143\u6b6a\u66f2',
		'Omen of the Ten': '\u5341\u798d\u7d76\u5091',
		'Brigade of the Sky': '\u84bc\u7a7a\u306e\u9a0e\u58eb',
		'Dawnbreak, Nightedge': '\u8d77\u6e90\u306e\u5149\u3001\u7d42\u7109\u306e\u95c7',
		'Chronogenesis': '\u6642\u7a7a\u8ee2\u751f',
		'Starforged Legends': '\u661f\u795e\u306e\u4f1d\u8aac',
		'Wonderland Dreams': '\u30ef\u30f3\u30c0\u30fc\u30e9\u30f3\u30c9\u30fb\u30c9\u30ea\u30fc\u30e0\u30ba',
		'Tempest of the Gods': '\u795e\u3005\u306e\u9a12\u5d50',
		'Rise of Bahamut': '\u30d0\u30cf\u30e0\u30fc\u30c8\u964d\u81e8',
		'Darkness Evolved': '\u30c0\u30fc\u30af\u30cd\u30b9\u30fb\u30a8\u30dc\u30eb\u30f4',
		'Storm Over Rivayle': '\u30ec\u30f4\u30a3\u30fc\u30eb\u306e\u65cb\u98a8',
		'Eternal Awakening': '\u5341\u5929\u899a\u9192',
		'Darkness Over Vellsar': '\u6697\u9ed2\u306e\u30a6\u30a7\u30eb\u30b5',
		'Renascent Chronicles': '\u30ea\u30ca\u30bb\u30f3\u30c8\u30fb\u30af\u30ed\u30cb\u30af\u30eb',
		'Classic': '\u30af\u30e9\u30b7\u30c3\u30af',
		'Basic': '\u30d9\u30fc\u30b7\u30c3\u30af',
		'Follower': '\u30d5\u30a9\u30ed\u30ef\u30fc',
		'Amulet': '\u30a2\u30df\u30e5\u30ec\u30c3\u30c8',
		'Spell': '\u30b9\u30da\u30eb',
		'Bronze': '\u30d6\u30ed\u30f3\u30ba\u30ec\u30a2',
		'Silver': '\u30b7\u30eb\u30d0\u30fc\u30ec\u30a2',
		'Gold': '\u30b4\u30fc\u30eb\u30c9\u30ec\u30a2',
		'Legendary': '\u30ec\u30b8\u30a7\u30f3\u30c9',
		'Include neutrals': '\u30cb\u30e5\u30fc\u30c8\u30e9\u30eb\u3092\u542b\u3080',
		'Yes': '\u542b\u3080',
		'Class cards only': '\u30af\u30e9\u30b9\u30ab\u30fc\u30c9\u3060\u3051',
		'Neutrals only': '\u30cb\u30e5\u30fc\u30c8\u30e9\u30eb\u3060\u3051',
		'Expansion': '\u30d1\u30c3\u30af',
		'Cost': '\u30b3\u30b9\u30c8',
		'Type': '\u30bf\u30a4\u30d7',
		'Rarity': '\u30ec\u30a2\u30ea\u30c6\u30a3',
		'Select a class': '\u30af\u30e9\u30b9\u3092\u9078\u3093\u3067',
		'Search card text': '\u30ab\u30fc\u30c9\u691c\u7d22',
		'Evo': '\u9032\u5316\u5f8c',
		'\u30d5\u30a9\u30ed\u30ef\u30fc': 'Follower',
		'\u30a2\u30df\u30e5\u30ec\u30c3\u30c8': 'Amulet',
		'\u30b9\u30da\u30eb': 'Spell',
		'\u30d6\u30ed\u30f3\u30ba\u30ec\u30a2': 'Bronze',
		'\u30b7\u30eb\u30d0\u30fc\u30ec\u30a2': 'Silver',
		'\u30b4\u30fc\u30eb\u30c9\u30ec\u30a2': 'Gold',
		'\u30ec\u30b8\u30a7\u30f3\u30c9': 'Legendary',
		'deckbuilder': '\u30c7\u30c3\u30ad\u4f5c\u6210',
		'resources': '\u30ea\u30bd\u30fc\u30b9',
		'emblems': '\u30a8\u30f3\u30d6\u30ec\u30e0',
		'flairs': '\u79f0\u53f7',
		'backgrounds': '\u80cc\u666f',
		'Uncensored Art': '\u30a4\u30e9\u30b9\u30c8\u30ca\u30fc\u30d5\u524d',
		'censored': '\u30a4\u30e9\u30b9\u30c8\u30ca\u30fc\u30d5',
		'Cards': '\u30ab\u30fc\u30c9',
		'Search': '\u691c\u7d22',
		'Filters': '\u30d5\u30a3\u30eb\u30bf',
		'Cancel': '\u30ad\u30e3\u30f3\u30bb\u30eb',
		'Show deck': '\u30c7\u30c3\u30ad\u8868\u793a',
		'Token': '\u30c8\u30fc\u30af\u30f3',
		'Forestcraft': '\u30a8\u30eb\u30d5',
		'Swordcraft': '\u30ed\u30a4\u30e4\u30eb',
		'Runecraft': '\u30a6\u30a3\u30c3\u30c1',
		'Dragoncraft': '\u30c9\u30e9\u30b4\u30f3',
		'Shadowcraft': '\u30cd\u30af\u30ed',
		'Bloodcraft': '\u30f4\u30a1\u30f3\u30d1\u30a4\u30a2',
		'Havencraft': '\u30d3\u30b7\u30e7\u30c3\u30d7',
		'Portalcraft': '\u30cd\u30e1\u30b7\u30b9',
		'animated': '\u30d7\u30ec\u30df\u30a2\u30e0'
	}

	@classmethod
	def _parse_trait(cls, trait: str) -> List[str]:
		return trait.split('\u30fb')

	@classmethod
	def _get_image_url_by_id(cls, id: str) -> str:
		return f"https://svgdb.me/assets/cards/jp/C_{id}.png"

	@classmethod
	def _get_evo_image_url_by_id(cls, id: str) -> str:
		return f"https://svgdb.me/assets/cards/jp/E_{id}.png"

	@classmethod
	def _get_voice_url_by_file(cls, voice: str) -> str:
		return f"https://svgdb.me/assets/audio/jp/{voice}"
