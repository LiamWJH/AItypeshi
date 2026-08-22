import mss
import mss.tools
from datetime import datetime
import pathlib
import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import os
import asyncio

output_dir = pathlib.Path().resolve() / "vision_mem"
output_dir.mkdir(exist_ok=True)

async def see():
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[0])

        base_name = datetime.now().strftime('%I-%M %p')
        file_path = output_dir / f"{base_name}.png"

        counter = 1
        while file_path.exists():
            file_path = output_dir / f"{base_name} ({counter}).png"
            counter += 1

        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(file_path))
        await asyncio.sleep(0.2) # base 0.2 wait to prevent cluster

def compare_images(path1, path2):
    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)

    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    structure_score, _ = ssim(gray1, gray2, full=True)

    hist1 = cv2.calcHist([img1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist2 = cv2.calcHist([img2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)
    color_score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    return structure_score, color_score

def delete_overlapping_sight():
    files = sorted(os.listdir(output_dir))
    itemN = len(files)
    for i in range(itemN - 1):
        a = str(output_dir / files[i])
        b = str(output_dir / files[i + 1])

        structure_score, color_score = compare_images(a, b)

        if structure_score > 0.97 and color_score > 0.97:
            os.remove(a)

async def main():
    while True:
        await see()
        delete_overlapping_sight()

asyncio.run(main())