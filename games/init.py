#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from ..utils import manager

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_CONFIG = os.path.join(PATH_ROOT, 'config.json')

cfgmgr = manager.ConfigManager(PATH_CONFIG)
