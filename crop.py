#!/usr/bin/env python3
"""
Batch crop and resize images to 1524x2200, convert to sRGB color space (pixel values), and save copies into a subfolder named "1524x2200" inside the selected folder.
Requires: Pillow, tkinter
"""
import os
import sys
import io
from tkinter import Tk, filedialog
from PIL import Image, ImageCms

target_width = 1524
target_height = 2200


def process_image(path, output_dir):
    with Image.open(path) as img:
        # Read original ICC profile bytes (if any)
        orig_icc = img.info.get('icc_profile')
        # Convert to RGB
        img = img.convert('RGB')
        # If original profile exists, convert pixel values to sRGB working space
        if orig_icc:
            try:
                src_profile = ImageCms.ImageCmsProfile(io.BytesIO(orig_icc))
                dst_profile = ImageCms.createProfile('sRGB')
                img = ImageCms.profileToProfile(img, src_profile, dst_profile, outputMode='RGB')
            except Exception as e:
                print(f"Warning: color profile conversion failed for {os.path.basename(path)}: {e}")
        
        # Scale to fit target dimensions for cropping
        w, h = img.size

        # Calculate scale factor to ensure the image is at least as large as the target dimensions
        scale = max(target_width / w, target_height / h)

        new_w = int(round(w * scale))
        new_h = int(round(h * scale))
        
        img = img.resize((new_w, new_h), Image.LANCZOS)
        
        # Center-crop to target dimensions
        left = (new_w - target_width) // 2
        top = (new_h - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        img = img.crop((left, top, right, bottom))

        # Prepare output path in output_dir
        filename = os.path.basename(path)
        base, ext = os.path.splitext(filename)
        out_name = f"{base}_{target_width}x{target_height}{ext}"
        out_path = os.path.join(output_dir, out_name)
        # Save (embed original ICC profile if present)
        save_kwargs = {}
        if orig_icc:
            save_kwargs['icc_profile'] = orig_icc
        img.save(out_path, **save_kwargs)
        print(f"Saved: {out_path}")


def main():
    # Select folder
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title='Select folder with images')
    if not folder:
        sys.exit('No folder selected.')
    # Create output subfolder
    output_dir = os.path.join(folder, f"{target_width}x{target_height}")
    os.makedirs(output_dir, exist_ok=True)
    # Supported extensions
    exts = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')
    for fname in os.listdir(folder):
        if fname.lower().endswith(exts):
            path = os.path.join(folder, fname)
            try:
                process_image(path, output_dir)
            except Exception as e:
                print(f"Error processing {fname}: {e}")

if __name__ == '__main__':
    main()
