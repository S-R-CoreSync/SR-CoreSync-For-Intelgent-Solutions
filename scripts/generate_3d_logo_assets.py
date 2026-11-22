#!/usr/bin/env python3
"""
generate_3d_logo_assets.py
Generates ultra-high-definition derived assets (WebP, PNG, Favicons, PWA icons)
from the official master 3D emblem (assets/sr-core-emblem-official.png).
"""

import os
from PIL import Image

def generate_assets():
    source_path = os.path.join("assets", "sr-core-emblem-official.png")
    if not os.path.exists(source_path):
        source_path = os.path.join("assets", "branding", "coresync-emblem-8k.png")
    
    print(f"Loading master source from: {source_path}")
    im = Image.open(source_path).convert("RGBA")
    w, h = im.size
    print(f"Master image size: {w}x{h}")

    targets = [
        ("assets/sr-core-emblem-official.webp", (384, 384), "WEBP", {"quality": 95, "method": 6}),
        ("assets/sr-core-emblem-official-384w.webp", (384, 384), "WEBP", {"quality": 95, "method": 6}),
        ("assets/sr-core-emblem-official-192w.webp", (192, 192), "WEBP", {"quality": 95, "method": 6}),
        ("assets/sr-core-emblem-official-sovereign.webp", (512, 512), "WEBP", {"quality": 95, "method": 6}),
        ("assets/sr-core-emblem-hd.png", (512, 512), "PNG", {}),
        ("assets/sr-core-emblem-256.png", (256, 256), "PNG", {}),
        ("assets/favicon-96.png", (96, 96), "PNG", {}),
        ("assets/favicon-180.png", (180, 180), "PNG", {}),
        ("assets/icon-192.png", (192, 192), "PNG", {}),
        ("assets/icon-512.png", (512, 512), "PNG", {}),
        ("assets/icon-maskable-192.png", (192, 192), "PNG", {}),
        ("assets/icon-maskable-512.png", (512, 512), "PNG", {}),
    ]

    for rel_path, size, fmt, params in targets:
        resized = im.resize(size, Image.Resampling.LANCZOS)
        out_path = os.path.abspath(rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        resized.save(out_path, fmt, **params)
        print(f"Generated: {rel_path} ({size[0]}x{size[1]}, {os.path.getsize(out_path)} bytes)")

    # Generate multi-size favicon.ico
    ico_path = os.path.abspath("favicon.ico")
    im.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"Generated: favicon.ico ({os.path.getsize(ico_path)} bytes)")

if __name__ == "__main__":
    generate_assets()
