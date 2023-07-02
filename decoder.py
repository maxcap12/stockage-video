import os
import shutil

import cv2
import re

SIZE_CONTENT_BITS = 32
SIZE_NAME_BITS = 10
X, Y = 854, 480


def get_images(title: str):
    if not os.path.isdir("frames"):
        os.mkdir("frames")

    video = cv2.VideoCapture(f"{title}.mp4")
    exist, frame = video.read()
    image_count = 0

    while exist:
        image_count += 1
        cv2.imwrite(f"frames/frame{image_count}.png", frame)
        exist, frame = video.read()

    return image_count


def get_content(im_id: int):
    image = cv2.imread(f"frames/frame{im_id}.png")
    return b"".join(b"1" if p[0] > 127 else b"0" for ligne in image for p in ligne)


def bin2str(val: bin):
    return "".join(chr(int(val[i*8:i*8+8], 2)) for i in range(len(val) // 8))


def decode_video(title: str):
    if not os.path.isdir("files"):
        os.mkdir("files")

    index = 0
    num_im = get_images(title)
    current_im = 0
    bits_to_read = 0
    is_name = True
    image_content = b""
    file_name = b""
    file_content = b""

    while current_im <= num_im:
        if index == 0:
            current_im += 1
            image_content = get_content(current_im)

        # on vient de lire le titre ou le content, donc faut determiner la taille du truc suivant
        if not bits_to_read:
            # check si on veut la taille du titre ou du content
            size_bits = SIZE_NAME_BITS if is_name else SIZE_CONTENT_BITS

            # check si les bits qui representent la taille debordent pas sur la prochaine image
            if X * Y - index < size_bits:
                image_content += get_content(current_im)
                current_im += 1
                bits_to_read = int(image_content[:size_bits], 2)
                index += size_bits - X * Y

            else:
                bits_to_read = int(image_content[index:index + size_bits], 2)
                index += size_bits

            # full pixels noir -> size 0 -> fin de la derniere image
            if not bits_to_read and current_im == num_im:
                break

        else:
            if is_name:
                if bits_to_read > X * Y - index:
                    file_name += image_content[index:]
                    bits_to_read -= X * Y - index
                    index = 0
                else:
                    file_name += image_content[index:index + bits_to_read]
                    index += bits_to_read
                    # check pas qu'on lise tout pile le nombre de bits qui a dans l'image,
                    # sinon l'index sera egal au dernier element +1
                    index %= X * Y
                    bits_to_read = 0
                    is_name = False

            else:
                if bits_to_read > X * Y - index:
                    file_content += image_content[index:]
                    bits_to_read -= X * Y - index
                    index = 0
                else:
                    file_content += image_content[index:index+bits_to_read]
                    index += bits_to_read
                    # check pas qu'on lise tout pile le nombre de bits qui a dans l'image,
                    # sinon l'index sera egal au dernier element +1
                    index %= X * Y
                    bits_to_read = 0
                    is_name = True

                    with open(f"files/{bin2str(file_name)}", "wb") as file:
                        # on doit split le content si il est trop long sinon overflow
                        # ca split en chunk de 32
                        # vu que file content c'est en bin, faut le transformer en str et enlever le prefix et les ""
                        # le dernier élement return c'est un str vide donc faut l'enlever
                        for chunk in re.findall(".{,1024}", str(file_content)[2:-1])[:-1]:
                            file.write(int(chunk, 2).to_bytes(len(chunk) // 8, byteorder='big'))

                    file_content = b""

    shutil.rmtree("frames")
