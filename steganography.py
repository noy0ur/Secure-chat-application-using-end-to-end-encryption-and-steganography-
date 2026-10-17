from PIL import Image

DELIMITER = "1111111111111110"

def text_to_binary(text):
    return ''.join(format(ord(i), '08b') for i in text)

def binary_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(c, 2)) for c in chars)

def hide_data(image_path, data, output_path):
    img = Image.open(image_path).convert("RGB")
    binary = text_to_binary(data) + DELIMITER

    pixels = list(img.getdata())

    # FIX: Check size
    if len(binary) > len(pixels) * 3:
        raise ValueError("Message too large for image")

    new_pixels = []
    index = 0

    for pixel in pixels:
        r, g, b = pixel

        if index < len(binary):
            r = (r & ~1) | int(binary[index])
            index += 1
        if index < len(binary):
            g = (g & ~1) | int(binary[index])
            index += 1
        if index < len(binary):
            b = (b & ~1) | int(binary[index])
            index += 1

        new_pixels.append((r, g, b))

    img.putdata(new_pixels)
    img.save(output_path)

def extract_data(image_path):
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    binary = ""

    for pixel in pixels:
        r, g, b = pixel
        binary += str(r & 1)
        binary += str(g & 1)
        binary += str(b & 1)

    end = binary.find(DELIMITER)

    if end != -1:
        binary = binary[:end]

    return binary_to_text(binary)