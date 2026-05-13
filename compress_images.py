#!/usr/bin/env python3
"""
批量压缩图片脚本
用法：把此文件和图片放同一目录，运行：
  python3 compress_images.py

会将所有 PNG/JPG 压缩为 max 1200px 宽、质量 85% 的 JPG
原图不动，压缩后的图覆盖同名 .png → .jpg
如果 PNG 有透明通道，保留为 PNG 格式压缩
"""

import os
import sys
from pathlib import Path
from PIL import Image

MAX_SIZE = 1200  # 最大边长
JPEG_QUALITY = 85
PNG_OPTIMIZE = True

target_dir = Path(__file__).parent
extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
skip_keywords = ['compress', 'script', '备份', '原图']

files = [f for f in target_dir.iterdir() if f.suffix in extensions and f.is_file()]
if not files:
    print('当前目录没有图片文件。')
    sys.exit(0)

print(f'找到 {len(files)} 张图片，开始压缩…\n')

for f in files:
    name_lower = f.name.lower()
    if any(k in name_lower for k in skip_keywords):
        print(f'  跳过: {f.name}')
        continue

    try:
        img = Image.open(f)
        orig_size = f.stat().st_size

        # 太大就等比缩放
        w, h = img.size
        if max(w, h) > MAX_SIZE:
            ratio = MAX_SIZE / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

        # 判断是否保留 PNG（有透明通道）
        if img.mode in ('RGBA', 'LA', 'P') and 'transparency' in img.info:
            out_name = f.stem + '.png'
            img.save(target_dir / out_name, 'PNG', optimize=PNG_OPTIMIZE)
        else:
            img = img.convert('RGB')
            out_name = f.stem + '.jpg'
            img.save(target_dir / out_name, 'JPEG', quality=JPEG_QUALITY, optimize=True)

        new_size = os.path.getsize(target_dir / out_name)
        ratio = 100 - (new_size / orig_size * 100) if orig_size > 0 else 0
        print(f'  {f.name} → {out_name}  ({orig_size//1024}KB → {new_size//1024}KB, -{ratio:.0f}%)')

    except Exception as e:
        print(f'  ❌ {f.name}: {e}')

print(f'\n完成。压缩后的图片已保存在 {target_dir}')
print(f'注意：原图未修改，如需删除原图请手动操作。')
