import json
import math
import statistics

import numpy
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image
import sys

def read_pgm(input_path):
    """Return a raster of integers from a PGM as a list of lists."""
    with open(input_path, "rb") as pgmf:
        assert pgmf.readline() == b'P5\n'
        (width, height) = [int(i) for i in pgmf.readline().split()]
        depth = int(pgmf.readline())
        assert depth <= 255
        raster = []
        for y in range(height):
            row = []
            for y in range(width):
                row.append(ord(pgmf.read(1)))
            raster.append(row)
        return raster


def flip_image(image_path, saved_location):
    """
    Flip or mirror the image
    @param image_path: The path to the image to edit
    @param saved_location: Path to save the cropped image
    """
    image_obj = Image.open(image_path)
    rotated_image = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
    rotated_image.save(saved_location)
    #rotated_image.show()


def show_mamo(input_path, x, y, d, max_width=1024):
    pgm = read_pgm(input_path)
    fig, ax = plt.subplots(1)
    ax.set_aspect('equal')
    # Show the image
    ax.imshow(pgm, cmap='gray', vmin=0, vmax=255)
    circ = Circle((x, 1024 - y), d)
    circ.fill = False
    ax.add_patch(circ)
    plt.show()


def augment_data():
    # {
    # "file_name_1": {
    #   type_background_tissue: "G",
    #   type: "NORM",
    #   coords: None
    # },
    # "file_name_2": {
    #   type_background_tissue: "F",
    #   type: "CIRC",
    #   coords: ("B", x, y, d)
    # }
    # }
    data = {}
    with open("Circles.txt", "r") as fin:
        lines = fin.read()
        for line in lines.splitlines():
            splitted_line = line.split()
            print(splitted_line)
            data[splitted_line[0] + ".pgm"] = {
                "type_background_tissue": splitted_line[1],
                "type": splitted_line[2],
                "coords": None if splitted_line[2] == "NORM" else [splitted_line[3], int(splitted_line[4]), int(splitted_line[5]), int(splitted_line[6])]
            }
    print(json.dumps(data, indent=2))
    old_data = data.copy()
    for file in old_data:
        flipped_file = file[:-4] + "_flipped" + file[-4:]
        flip_image(f"mamo/{file}", f"mamo/{flipped_file}")
        data[flipped_file] = data[file]
        if data[file]["type"] == "NORM":
            continue
        data[flipped_file]["coords"][1] = 1024 - data[file]["coords"][1]
    with open("mamo.json", "w") as fout:
        fout.write(json.dumps(data, indent=2))


'''
show_mamo("mamo/mdb115.pgm")
flip_image("mamo/mdb115.pgm", "mamo/mdb115_flipped.pgm")
show_mamo("mamo/mdb115_flipped.pgm")
'''

#augment_data()
#show_mamo("mamo/mdb090.pgm", 510, 547, 49)
#flip_image("mamo/mdb090.pgm", "mamo/mdb090_flipped.pgm")
#show_mamo("mamo/mdb090_flipped.pgm", 1024 - 510, 547, 49)
#augment_data()


def norm_image(input_path, output_path, data_entry):
    with open(input_path, "rb") as pgmf:
        assert pgmf.readline() == b'P5\n'
        (width, height) = [int(i) for i in pgmf.readline().split()]
        depth = int(pgmf.readline())
        assert depth <= 255
        raster = []
        for y in range(height):
            row = []
            for y in range(width):
                row.append(ord(pgmf.read(1)))
            raster.append(row)
    col_sums = []
    for j in range(len(raster[0])):
        col_sums.append(sum([raster[i][j] for i in range(len(raster))]))
    # tgs = [col_sums[i + 1] - col_sums[i] for i in range(len(col_sums) - 1)]
    # start_tgs = 0
    # end_tgs = len(tgs) - 1
    # while start_tgs < len(tgs):
    #     if tgs[start_tgs] < 3000:
    #         start_tgs += 1
    #     else:
    #         break
    # while end_tgs >= 0:
    #     if tgs[end_tgs] < 3000:
    #         end_tgs -= 1
    #     else:
    #         break
    # print(tgs)
    # plt.plot(col_sums[start_tgs : end_tgs + 1])
    # plt.show()
    # plt.plot(tgs[start_tgs : end_tgs + 1])
    # plt.show()

    #print(col_sums)
    #mean = sum(col_sums) / len(col_sums)
    #print(mean)
    #deviation = statistics.stdev(col_sums)
    #print(deviation)
    index_col_start = 0
    index_col_end = len(raster[0]) - 1
    while index_col_start < len(raster[0]):
        col_sum = col_sums[index_col_start]
        if col_sum > depth:
            break
        index_col_start += 1
    while index_col_end >= 0:
        col_sum = col_sums[index_col_end]
        if col_sum > depth:
            break
        index_col_end -= 1
    data_entry["left_crop"] = index_col_start
    data_entry["right_crop"] = index_col_end
    new_raster = [[raster[i][j] for j in range(index_col_start, index_col_end + 1)] for i in range(len(raster))]
    with open(output_path, "wb") as fout:
        fout.write(b"P5\n")
        fout.write(f"{index_col_end - index_col_start + 1} {height}\n".encode())
        fout.write(f"{depth}\n".encode())
        for i in range(len(new_raster)):
            for j in range(len(new_raster[i])):
                fout.write(new_raster[i][j].to_bytes(1, sys.byteorder))


# with open("mamo.json", "r") as fin:
#     data = json.loads(fin.read())
# for file in data:
#     norm_image(f"mamo/{file}", f"norm_mamo/{file}", data[file])
# with open("mamo_norm.json", "w") as fout:
#     fout.write(json.dumps(data, indent=2))

show_mamo("norm_mamo/mdb001.pgm", 0, 0, 0)