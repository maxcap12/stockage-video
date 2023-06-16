from upload_video import upload
from encoder import encode_files, get_bits
import time

t = time.time()

encode_files(["image.jpg", "test"], "video")

print("--- %s seconds ---" % (time.time() - t))
