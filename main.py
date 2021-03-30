import numpy
import matplotlib.pylab as plt
from matplotlib.patches import Circle

def read_pgm(pgmf):
    """Return a raster of integers from a PGM as a list of lists."""
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


with open("mamo/mdb115.pgm", "rb") as fin:
    print(pgm := read_pgm(fin))
    fig, ax = plt.subplots(1)
    x = 461
    y = 532
    d = 117
    ax.set_aspect('equal')
    # Show the image
    ax.imshow(pgm, cmap='gray', vmin=0, vmax=255)
    circ = Circle((y, 1024 - x), d)
    circ.fill = False
    ax.add_patch(circ)
    plt.show()
