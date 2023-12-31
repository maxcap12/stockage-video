import shutil

from PIL import Image
import cv2
import os

SIZE_CONTENT_BITS = 32
SIZE_NAME_BITS = 10
X, Y = 854, 480
BIN = {
    "0": "0000", "1": "0001",
    "2": "0010", "3": "0011",
    "4": "0100", "5": "0101",
    "6": "0110", "7": "0111",
    "8": "1000", "9": "1001",
    "a": "1010", "b": "1011",
    "c": "1100", "d": "1101",
    "e": "1110", "f": "1111"
}


def get_bits(path: str):

    with open(path, "rb") as file:
        content = file.read().hex()

    return "".join("{}".format(BIN[char]) for char in content)


"""
Initial function
def write_content(image: Image, index: int, content: str, image_count: int):
    pixels = image.load()
    # peut-etre check ici pour la taille du content
    for b in content:
        if index == X * Y:
            image.save(f"frames/frame{image_count}.png")
            image_count += 1
            image = Image.new("1", (X, Y))
            pixels = image.load()
            index = 0

        pixels[index % X, index // X] = 0 if b == '0' else 255
        index += 1

    return image, image_count, index
"""


def write_content(image: Image, index: int, content: str, image_count: int):
    pixels = image.load()

    if len(content) > X * Y - index:
        additional_content = content[X * Y - index:]
        content = content[:X * Y - index]

    x = index % X
    y = index // X

    for b in content:
        if x == X:
            x = 0
            y += 1

        pixels[x, y] = 0 if b == '0' else 255
        x += 1

    if "additional_content" in locals().keys():
        image.save(f"frames/frame{image_count}.png")
        return write_content(Image.new("1", (X, Y)), 0, additional_content, image_count + 1)

    return image, image_count, index + len(content)


def str2bin(string: str):
    return "".join("{0:08b}".format(ord(x), 'b') for x in string)


def int2bin(val: int, size: int):
    return f"{val:0>{size}b}"


def generate_video(num_images: int, title: str):
    video = cv2.VideoWriter(f"{title}.mp4", 0x7634706d, 1, (X, Y))

    for i in range(num_images):
        video.write(cv2.imread(f"frames/frame{i + 1}.png"))

    video.release()


def encode_files(files: list[str], title: str):
    if not os.path.isdir("frames"):
        os.mkdir("frames")

    image = Image.new("1", (X, Y))
    index = 0
    image_count = 1

    for file in files:
        name = str2bin(file)
        name_size = int2bin(len(name), SIZE_NAME_BITS)
        image, image_count, index = write_content(image, index, name_size, image_count)
        image, image_count, index = write_content(image, index, name, image_count)

        content = get_bits(file)
        content_size = int2bin(len(content), SIZE_CONTENT_BITS)
        image, image_count, index = write_content(image, index, content_size, image_count)
        image, image_count, index = write_content(image, index, content, image_count)

    image.save(f"frames/frame{image_count}.png")
    generate_video(image_count, title)
    shutil.rmtree("frames")

# 1.1981852054595947
# 0.899057149887085
# 0.758840799331665
