import math
from PIL import Image, ImageDraw, ImageFont
import random
import moviepy.video.io.ImageSequenceClip
import os

POPULATION_SIZE = 400
LINE_LENGTH = 101
DECIMATION = 60
NO_CHILDREN = 40
MUTATION_SEVERITY = 4
ROT_IMPORTANCE = 100
GEN = 0
MAX_GEN = 50
SERIES_DATA = []

def chromosome_create(steps):
    chromosome = ''
    for i in range(steps):
        r = random.randint(0, 3600)
        bin_r = bin(r)[2:].zfill(12)
        chromosome += bin_r

    return chromosome


def split(split_str, offset):
    return [split_str[indice:indice + offset] for indice in range(0, len(split_str), offset)]


def decode_chromosome(chromosome, length):
    dec = [int(s, 2) for s in split(chromosome, length)]
    rot = [math.radians(d/10) for d in dec]
    return rot


def points(rot, start_pos, length):
    pts = [start_pos]
    for r in rot:
        x = pts[-1][0] + math.cos(r) * length
        y = pts[-1][1] + math.sin(r) * length
        pts.append((x, y))
    draw_pts = [(int(p[0]), int(p[1])) for p in pts]
    return pts, draw_pts


def fitness(start, end):
    return (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2


def rotations_fit(rot):
    total = 0
    for i in range(1, len(rot)):
        total += (rot[i] - rot[i-1]) ** 4
    return total


def draw_organism(imgd, draw, color):
    for i in range(len(draw) - 1):
        imgd.line([draw[i], draw[i+1]], fill=color)


def create_child(parent_1, parent_2, start, end, mutate):
    dec_1 = [s for s in split(parent_1["Chromosome"], 12)]
    dec_2 = [s for s in split(parent_2["Chromosome"], 12)]

    child_dec = []

    for i in range(len(dec_1)):
        if random.randint(0, 1) == 1:
            child_dec.append(dec_1[i])
        else:
            child_dec.append(dec_2[i])

    ch_1 = ""

    for d in child_dec:
        ch_1 += d

    if mutate:
        for i in range(MUTATION_SEVERITY):
            r = random.randint(0, len(ch_1) - 2)
            if ch_1[r] == "1":
                ch_1 = ch_1[:r] + "0" + ch_1[r+1:]
            else:
                ch_1 = ch_1[:r] + "1" + ch_1[r+1:]

    rot = decode_chromosome(ch_1, 12)
    pts, draw_pts = points(rot, start, LINE_LENGTH)

    child_dict = {
        "Fitness": int(fitness(pts[-1], end)) + int(rotations_fit(rot)) * ROT_IMPORTANCE,
        "Chromosome": ch_1,
        "Rotations": rot,
        "Points": pts,
        "Drawing": draw_pts
    }

    return child_dict


def next_generation(population, start, end):

    global GEN
    GEN += 1

    w, h = 2000, 2000

    end_point = [(end[0] - 25, end[1] - 25), (end[0] + 25, end[1] + 25)]
    start_point = [(start[0] - 25, start[1] - 25), (start[0] + 25, start[1] + 25)]

    if(GEN > MAX_GEN):
        SERIES_DATA.append(population[0]["Fitness"])
        return

    decimated = population[:DECIMATION]

    new_organisms = []
    for i in range(NO_CHILDREN):
        new_organisms.append(create_child(random.choice(decimated), random.choice(decimated), start, end, False))
    for i in range(POPULATION_SIZE - NO_CHILDREN - DECIMATION):
        new_organisms.append(create_child(random.choice(decimated), random.choice(decimated), start, end, True))

    decimated.extend(new_organisms)

    population = sorted(decimated, key=lambda j: j["Fitness"])
    if GEN % 1 == 0:
        img = Image.new("RGB", (w, h), (255, 255, 255))

        # create rectangle image
        imgd = ImageDraw.Draw(img)

        for i in range(len(population)):
            draw_organism(imgd, population[i]["Drawing"], "#dddddd")

        draw_organism(imgd, population[0]["Drawing"], "#ff0000")

        imgd.rectangle(start_point, fill="#000000")
        imgd.rectangle(end_point, fill="#000000")

        font = ImageFont.truetype("Lato.ttf", 32)
        imgd.text((1600, 50), f"GENERATION {GEN}", (0, 0, 0), font=font)

        img.save(f"images/Test{str(GEN).zfill(3)}.jpg", "JPEG")

    print(population[0]["Fitness"])
    next_generation(population, start, end)


def first_generation(imgd, img, start, end):
    population = []

    global GEN
    GEN = 1

    for i in range(POPULATION_SIZE):
        ch_1 = chromosome_create(25)
        rot = decode_chromosome(ch_1, 12)
        pts, draw_pts = points(rot, start, LINE_LENGTH)

        ch_dict = {
            "Fitness": int(fitness(pts[-1], end)) + int(rotations_fit(rot)) * ROT_IMPORTANCE,
            "Chromosome": ch_1,
            "Rotations": rot,
            "Points": pts,
            "Drawing": draw_pts
        }

        population.append(ch_dict)

    population = sorted(population, key=lambda j: j["Fitness"])

    for i in range(len(population)):
        draw_organism(imgd, population[i]["Drawing"], "#dddddd")

    draw_organism(imgd, population[0]["Drawing"], "#ff0000")

    font = ImageFont.truetype("Lato.ttf", 32)
    imgd.text((1600, 50), f"GENERATION {GEN}", (0, 0, 0), font=font)
    img.save(f"images/Test{str(GEN).zfill(3)}.jpg", "JPEG")

    next_generation(population, start, end)


def main():
    w, h = 2000, 2000
    end = (1900, 1900)
    start = (100, 100)

    end_point = [(end[0] - 25, end[1] - 25), (end[0] + 25, end[1] + 25)]
    start_point = [(start[0] - 25, start[1] - 25), (start[0] + 25, start[1] + 25)]

    # creating new Image object
    img = Image.new("RGB", (w, h), (255, 255, 255))

    # create rectangle image
    imgd = ImageDraw.Draw(img)
    imgd.rectangle(start_point, fill="#000000")
    imgd.rectangle(end_point, fill="#000000")

    first_generation(imgd, img, start, end)

    image_folder = "images"
    fps = 20
    image_files = [image_folder + '/' + img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(f"{SERIES_DATA[0]}.mp4")

main()