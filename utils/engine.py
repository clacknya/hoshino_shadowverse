#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Type, Tuple, List, Dict, Generator, NoReturn

import os
import re
import logging
import inspect
import importlib

from .engines import _base as base

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_ENGINES = os.path.dirname(inspect.getfile(base))

def each_module(plugins_dir: str) -> Generator[str, None, None]:
	plugins_dir_rel = os.path.relpath(plugins_dir, os.getcwd())
	module_path_rel = plugins_dir_rel.replace(os.sep, '.')
	pattern = re.compile(r'([_A-Z0-9a-z]+)(?:.py)?')
	for name in os.listdir(plugins_dir):
		path = os.path.join(plugins_dir, name)
		if os.path.isfile(path) and \
			(name.startswith('_') or not name.endswith('.py')):
			continue
		if os.path.isdir(path):
			continue
		m = pattern.match(name)
		if not m:
			continue
		yield f"{module_path_rel}.{m.group(1)}"

def load_engines() -> NoReturn:
	_modules.clear()
	_engines.clear()
	for module_name in each_module(PATH_ENGINES):
		module = importlib.import_module(module_name, package='.')
		_modules.append(module)
		_engines.update(dict(filter(
			lambda x: issubclass(x[1], base.BaseEngine),
			inspect.getmembers(module, inspect.isclass)
		)))

def reload_engines() -> NoReturn:
	_engines.clear()
	for module in _modules:
		importlib.reload(module)
		_engines.update(dict(filter(
			lambda x: issubclass(x[1], base.BaseEngine),
			inspect.getmembers(module, inspect.isclass)
		)))

_modules = []
_engines = {}

load_engines()

def list_engines() -> List[Tuple[str, str]]:
	return [(k, v.SOURCE) for k, v in _engines.items()]

def get_engines() -> Dict[str, Type[base.BaseEngine]]:
	return _engines

def get_engine(name: str) -> Type[base.BaseEngine]:
	return _engines.get(name)
