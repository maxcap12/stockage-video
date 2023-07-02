from upload_video import upload
from encoder import encode_files, get_bits, str2bin
from decoder import decode_video
import cv2
import time

t = time.time()

encode_files(["test", "image.jpg"], "video")

print(f"encoding: {time.time() - t}")

t = time.time()

decode_video("video")

print(f"decoding: {time.time() - t}")
