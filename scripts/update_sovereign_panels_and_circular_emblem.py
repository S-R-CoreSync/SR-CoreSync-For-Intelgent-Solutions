#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
S&R CoreSync For Intelligent Solutions - Sovereign Platform
PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
==============================================================================

update_sovereign_panels_and_circular_emblem.py
==============================================
Official Sovereign 3D Emblem Pipeline:
1. Generates intrinsically circular, transparent 3D master emblem with polished gold bezel
   from the authentic chrome SR 3D monogram source.
2. Regenerates derived emblem sizes (WebP, PNG, favicon, PWA icons).
3. Seamlessly replaces the legacy emblem in the 3 sovereign panels:
   - founder-banner-salim (at exact cx=322, cy=240, d=310)
   - founder-banner-raed (at exact cx=1960, cy=292, d=252)
   - sr-emblem-gold-luxury (at exact cx=514, cy=264, d=346)
   - All 29 localized i18n variants.
4. Generates all responsive variants (4K, 2560, 1280, 640, WebP, JPG) with quality=82
   to strictly satisfy the 450 KB performance budget.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from apply_root_emblem_fix import run

if __name__ == "__main__":
    run()
