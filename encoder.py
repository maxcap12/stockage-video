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
    content = ""
    buffer = 2 ** 10

    with open(path, "rb") as file:
        while chunk := file.read(buffer):
            content += chunk.hex()

    return "".join("{}".format(BIN[char]) for char in content)


def write_content(image: Image, index: int, content: str, image_count: int):
    pixels = image.load()

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


def str2bin(string: str):
    return "".join("{0:08b}".format(ord(x), 'b') for x in string)


def int2bin(val: int, size: int):
    return f"{val:0>{size}b}"


def images2video(num_images: int):
    pass


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

        print(len(content)/8)

    image.save(f"frames/frame{image_count}.png")
    images2video(0)
