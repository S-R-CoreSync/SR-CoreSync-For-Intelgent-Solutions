#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_sovereign_panels_and_circular_emblem.py
1. Generates intrinsically circular, transparent 3D master emblem with polished gold bezel.
2. Regenerates derived emblem sizes (WebP, PNG, favicon).
3. Seamlessly replaces the old emblem in the 3 sovereign panels:
   - founder-banner-salim (and all scaled/localized variants)
   - founder-banner-raed (and all scaled/localized variants)
   - sr-emblem-gold-luxury (and all scaled variants)
"""

import os
import glob
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT, "assets")

def create_circular_master_emblem():
    print("-> Creating intrinsically circular master 3D emblem with luxury gold bezel...")
    src_path = os.path.join(ASSETS_DIR, "branding", "coresync-emblem-8k.png")
    if not os.path.exists(src_path):
        src_path = os.path.join(ASSETS_DIR, "sr-core-emblem-official.png")
    
    master = Image.open(src_path).convert("RGBA")
    w, h = master.size
    
    # Calculate center and radius
    # In 2048x2048, center is (1024, 1064), radius is ~840
    # In 1024x1024, center is (512, 532), radius is ~420
    scale = w / 1024.0
    cx = int(512 * scale)
    cy = int(532 * scale)
    radius = int(420 * scale)

    # Circular mask with smooth anti-aliased edge
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(int(2 * scale)))

    # Luxury polished gold double ring border
    ring = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    line1 = max(3, int(6 * scale))
    line2 = max(2, int(3 * scale))
    rd.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(212, 175, 55, 240), width=line1)
    offset = max(4, int(7 * scale))
    rd.ellipse((cx - radius + offset, cy - radius + offset, cx + radius - offset, cy + radius - offset), outline=(243, 223, 186, 160), width=line2)

    # Compose
    circular_full = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    circular_full.paste(master, (0, 0), mask)
    circular_full = Image.alpha_composite(circular_full, ring)

    # Crop to exact circular bounds
    pad = int(3 * scale)
    cropped = circular_full.crop((cx - radius - pad, cy - radius - pad, cx + radius + pad, cy + radius + pad))
    
    # Resize to canonical 1024x1024 master
    out_master = cropped.resize((1024, 1024), Image.Resampling.LANCZOS)
    out_path = os.path.join(ASSETS_DIR, "sr-core-emblem-official.png")
    out_master.save(out_path, "PNG", optimize=True)
    print(f"Saved circular master emblem: {out_path} (1024x1024)")
    return out_master

def make_coin(master_im, diameter):
    return master_im.resize((diameter, diameter), Image.Resampling.LANCZOS)

def update_banner_emblem(img_path, center_x, center_y, diameter, coin):
    if not os.path.exists(img_path):
        return False
    
    with Image.open(img_path) as im:
        orig_w, orig_h = im.size
        is_rgba = im.mode == 'RGBA'
        banner = im.convert('RGBA')
    
    # Calculate scale relative to baseline (2560 for founder, 1024 for luxury)
    # The caller provides coordinates for the baseline image
    cx, cy, d = center_x, center_y, diameter
    
    resized_coin = coin.resize((d, d), Image.Resampling.LANCZOS)
    top_left = (int(cx - d / 2), int(cy - d / 2))
    banner.paste(resized_coin, top_left, resized_coin)
    
    # Save back in original format and quality
    fmt = "JPEG" if img_path.lower().endswith(('.jpg', '.jpeg')) else "WEBP"
    if fmt == "JPEG":
        banner.convert("RGB").save(img_path, "JPEG", quality=95, optimize=True)
    else:
        banner.save(img_path, "WEBP", quality=95, method=6)
    return True

def generate_scaled_variants(base_2560_path, base_name, is_jpg=True):
    with Image.open(base_2560_path) as im:
        im_rgb = im.convert("RGB")
        
        # 4K (3840x2160)
        im_4k = im_rgb.resize((3840, 2160), Image.Resampling.LANCZOS)
        p_4k_jpg = os.path.join(ASSETS_DIR, f"{base_name}-4k.jpg")
        p_4k_webp = os.path.join(ASSETS_DIR, f"{base_name}-4k.webp")
        im_4k.save(p_4k_jpg, "JPEG", quality=95, optimize=True)
        im_4k.save(p_4k_webp, "WEBP", quality=95, method=6)
        
        # 2560 WebP
        p_2560_webp = os.path.join(ASSETS_DIR, f"{base_name}-2560.webp")
        im_rgb.save(p_2560_webp, "WEBP", quality=95, method=6)
        
        # Base WebP (2560)
        p_base_webp = os.path.join(ASSETS_DIR, f"{base_name}.webp")
        im_rgb.save(p_base_webp, "WEBP", quality=95, method=6)
        
        # 1280 (1280x720)
        im_1280 = im_rgb.resize((1280, 720), Image.Resampling.LANCZOS)
        p_1280_jpg = os.path.join(ASSETS_DIR, f"{base_name}-1280.jpg")
        p_1280_webp = os.path.join(ASSETS_DIR, f"{base_name}-1280.webp")
        im_1280.save(p_1280_jpg, "JPEG", quality=92, optimize=True)
        im_1280.save(p_1280_webp, "WEBP", quality=92, method=6)

        # 640 (640x360)
        im_640 = im_rgb.resize((640, 360), Image.Resampling.LANCZOS)
        p_640_jpg = os.path.join(ASSETS_DIR, f"{base_name}-640.jpg")
        p_640_webp = os.path.join(ASSETS_DIR, f"{base_name}-640.webp")
        im_640.save(p_640_jpg, "JPEG", quality=90, optimize=True)
        im_640.save(p_640_webp, "WEBP", quality=90, method=6)

def update_all_sovereign_panels(master_emblem):
    print("-> Updating the 3 Sovereign Panels with official new 3D emblem...")
    
    # 1. Salim Banner (2560x1440) - cx=324, cy=274, diameter=452
    coin_salim = make_coin(master_emblem, 452)
    salim_base = os.path.join(ASSETS_DIR, "founder-banner-salim.jpg")
    update_banner_emblem(salim_base, 324, 274, 452, coin_salim)
    print("Updated master founder-banner-salim.jpg")
    generate_scaled_variants(salim_base, "founder-banner-salim")
    print("Generated all scaled variants for founder-banner-salim")

    # Localized Salim Banners (29 locales)
    for p in glob.glob(os.path.join(ASSETS_DIR, "i18n", "*", "founder-banner-salim.jpg")):
        update_banner_emblem(p, 324, 274, 452, coin_salim)
        # Also update webp and 4k if present
        p_webp = p.replace(".jpg", ".webp")
        if os.path.exists(p_webp):
            update_banner_emblem(p_webp, 324, 274, 452, coin_salim)
        p_4k = p.replace(".jpg", "-4k.jpg")
        if os.path.exists(p_4k):
            scale_4k = 3840 / 2560
            coin_4k = make_coin(master_emblem, int(452 * scale_4k))
            update_banner_emblem(p_4k, int(324 * scale_4k), int(274 * scale_4k), int(452 * scale_4k), coin_4k)
    print("Updated all localized Salim banners")

    # 2. Raed Banner (2560x1440) - cx=2211, cy=336, diameter=426
    coin_raed = make_coin(master_emblem, 426)
    raed_base = os.path.join(ASSETS_DIR, "founder-banner-raed.jpg")
    update_banner_emblem(raed_base, 2211, 336, 426, coin_raed)
    print("Updated master founder-banner-raed.jpg")
    generate_scaled_variants(raed_base, "founder-banner-raed")
    print("Generated all scaled variants for founder-banner-raed")

    # Localized Raed Banners (29 locales)
    for p in glob.glob(os.path.join(ASSETS_DIR, "i18n", "*", "founder-banner-raed.jpg")):
        update_banner_emblem(p, 2211, 336, 426, coin_raed)
        p_webp = p.replace(".jpg", ".webp")
        if os.path.exists(p_webp):
            update_banner_emblem(p_webp, 2211, 336, 426, coin_raed)
        p_4k = p.replace(".jpg", "-4k.jpg")
        if os.path.exists(p_4k):
            scale_4k = 3840 / 2560
            coin_4k = make_coin(master_emblem, int(426 * scale_4k))
            update_banner_emblem(p_4k, int(2211 * scale_4k), int(336 * scale_4k), int(426 * scale_4k), coin_4k)
    print("Updated all localized Raed banners")

    # 3. Luxury Cinematic Emblem Banner (1024x576) - cx=511, cy=291, diameter=426
    coin_lux = make_coin(master_emblem, 426)
    lux_jpg = os.path.join(ASSETS_DIR, "sr-emblem-gold-luxury.jpg")
    update_banner_emblem(lux_jpg, 511, 291, 426, coin_lux)
    
    lux_webp = os.path.join(ASSETS_DIR, "sr-emblem-gold-luxury.webp")
    if os.path.exists(lux_webp):
        update_banner_emblem(lux_webp, 511, 291, 426, coin_lux)
        
    lux_4k = os.path.join(ASSETS_DIR, "sr-emblem-gold-luxury-4k.jpg")
    if os.path.exists(lux_4k):
        with Image.open(lux_4k) as im4:
            w4, h4 = im4.size
        scale_lux = w4 / 1024.0
        coin_lux_4k = make_coin(master_emblem, int(426 * scale_lux))
        update_banner_emblem(lux_4k, int(511 * scale_lux), int(291 * scale_lux), int(426 * scale_lux), coin_lux_4k)
    print("Updated sr-emblem-gold-luxury and its variants")

def main():
    circular_master = create_circular_master_emblem()
    
    # Regenerate all standard derived sizes (WebP, PNG, Favicons)
    print("-> Regenerating derived 3D logo assets...")
    import generate_3d_logo_assets
    generate_3d_logo_assets.generate_assets()
    
    # Update the 3 sovereign panels
    update_all_sovereign_panels(circular_master)
    print("\n[SUCCESS] All sovereign panels and circular emblems successfully updated!")

if __name__ == "__main__":
    main()
