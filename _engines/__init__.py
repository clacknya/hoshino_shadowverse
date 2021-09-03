#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Type, Tuple, List, Dict, Generator, NoReturn

import os
import re
import inspect
import importlib

from . import _base as base

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_ROOT_REL = os.path.relpath(PATH_ROOT, os.getcwd())
PATH_MODULE_REL = PATH_ROOT_REL.replace(os.sep, '.')

def each_module() -> Generator[str, None, None]:
	pattern = re.compile(r'([_A-Z0-9a-z]+)(?:.py)?')
	for name in os.listdir(PATH_ROOT):
		path = os.path.join(PATH_ROOT, name)
		if os.path.isfile(path) and \
			(name.startswith('_') or not name.endswith('.py')):
			continue
		if os.path.isdir(path):
			continue
		m = pattern.match(name)
		if not m:
			continue
		yield f"{PATH_MODULE_REL}.{m.group(1)}"

def load_engines() -> NoReturn:
	_modules.clear()
	_engines.clear()
	for module_name in each_module():
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
