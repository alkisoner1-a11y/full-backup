import os
import sys
import subprocess
import shutil
import re

try:
    from PIL import Image
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

def move_assets_and_cleanup(base_dir):
    public_html_dir = os.path.join(base_dir, "public_html")
    assets_src = os.path.join(public_html_dir, "assets")
    assets_dest = os.path.join(base_dir, "assets")
    
    if os.path.exists(assets_src):
        if os.path.exists(assets_dest):
            shutil.rmtree(assets_dest)
        shutil.move(assets_src, base_dir)
        print("Moved assets")
    
    if os.path.exists(public_html_dir):
        shutil.rmtree(public_html_dir)
        print("Removed public_html")

def lowercase_rename(dir_path):
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            lower_name = name.lower()
            if lower_name != name:
                os.rename(os.path.join(root, name), os.path.join(root, lower_name))
                print(f"Renamed {name} to {lower_name}")
        for name in dirs:
            lower_name = name.lower()
            if lower_name != name:
                os.rename(os.path.join(root, name), os.path.join(root, lower_name))
                print(f"Renamed {name} to {lower_name}")

def optimize_images(dir_path):
    for root, _, files in os.walk(dir_path):
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png']:
                img_path = os.path.join(root, name)
                webp_path = os.path.splitext(img_path)[0] + '.webp'
                
                try:
                    with Image.open(img_path) as img:
                        if img.mode != 'RGB' and img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        
                        if img.width > 1920:
                            ratio = 1920.0 / img.width
                            new_height = int(img.height * ratio)
                            img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
                        
                        img.save(webp_path, 'WEBP', quality=85)
                        print(f"Optimized to WebP: {webp_path}")
                        
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")
                else:
                    os.remove(img_path)
                    print(f"Deleted original: {img_path}")

def update_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove 'public_html/' prefix
    content = content.replace('public_html/assets/', 'assets/')

    # 2. Lowercase and change extension
    def process_asset_path(match):
        path = match.group(0).lower()
        path = re.sub(r'\.(jpg|jpeg|png)$', '.webp', path)
        return path

    content = re.sub(r'assets/[^"\'>]+', process_asset_path, content)

    # 3. Add loading="lazy" except for cursorimage
    def process_img_tag(match):
        img_tag = match.group(0)
        if 'loading=' not in img_tag and 'cursorimage' not in img_tag.lower():
            if img_tag.endswith('/>'):
                return img_tag[:-2] + ' loading="lazy" />'
            else:
                return img_tag[:-1] + ' loading="lazy" >'
        return img_tag

    content = re.sub(r'<img\s+[^>]+>', process_img_tag, content)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated index.html")

base = "/Users/alkisgeorgopoulossakiri/Downloads/full-backup"
move_assets_and_cleanup(base)
assets_path = os.path.join(base, "assets")
lowercase_rename(assets_path)
optimize_images(assets_path)
update_html(os.path.join(base, "index.html"))
print("Optimization complete.")
