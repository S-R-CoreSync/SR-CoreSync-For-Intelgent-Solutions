# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_lang import apply
from translations_fi import FI
print('fi replacements:', apply('fi', FI))
