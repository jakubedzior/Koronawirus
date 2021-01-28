import cv2
import numpy as np
from PIL import Image
import os


def convertImage(path, threshold):
    img = Image.open(path)
    pix = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pix[x, y][0] < threshold or pix[x, y][1] < threshold or pix[x, y][2] < threshold:
                pix[x, y] = (0, 0, 0, 255)
            else:
                pix[x, y] = (255, 255, 255, 255)
    img.save((path[:-4] + 'png') if path[-5] == '.' else(path[:-3] + 'png'))


def scaleImage(path, width, height):
    img = cv2.imread(path)
    if width == img.shape[1] and height == img.shape[0]:
        return
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, resized)


def cropImage(path, pos, size):
    img = cv2.imread(path)
    crop_img = img[pos[1]:pos[1]+size[1], pos[0]:pos[0]+size[0]]
    # cv2.imshow("cropped", crop_img)
    cv2.imwrite("temp.png", crop_img)
    # cv2.waitKey(0)


def readNumber(path_with_file, folder_with_templates):
    method = cv2.TM_CCOEFF_NORMED

    nums = []
    for num in range(10):
        nums.append(cv2.imread(
            f'{folder_with_templates}\\{num}.png', cv2.IMREAD_UNCHANGED))

    big_picture = cv2.imread(path_with_file, cv2.IMREAD_UNCHANGED)

    finals = {0: [], 1: [], 2: [], 3: [], 4: [],
              5: [], 6: [], 7: [], 8: [], 9: []}

    for index, num in enumerate(nums):
        result = cv2.matchTemplate(num, big_picture, method)

        locs = {}
        locs['all'] = np.where(result >= .75)[1].tolist()
        locs['all'].sort()

        if len(locs['all']) == 0:
            continue
        elif len(locs['all']) == 1:
            finals[index].append(locs['all'][0])
        else:
            solution = 0
            for i, loc in enumerate(locs['all']):
                if i == 0:
                    continue
                locs.setdefault(solution, [])
                if - 30 < loc - locs['all'][i - 1] < 30:
                    locs[solution].append(locs['all'][i - 1])
                else:
                    locs[solution].append(locs['all'][i - 1])
                    if i + 1 != len(locs['all']):
                        solution += 1
            locs[solution].append(locs['all'][-1])

        for key in locs:
            if key == 'all':
                continue
            finals[index].append(sum(locs[key]) // len(locs[key]))

    # print(finals)
    theNumber = ''
    while True:
        results = 0
        min_ = 100_000
        min_key = None
        for key in finals:
            lenght = len(finals[key])
            results += lenght
            if lenght > 0:
                if finals[key][0] < min_:
                    min_ = finals[key][0]
                    min_key = key
        if results == 0:
            return None
        theNumber += str(min_key)
        finals[min_key].pop(0)
        results -= 1
        if results == 0:
            break

    return int(theNumber)


if __name__ == '__main__':
    os.chdir(os.getcwd() + '\\Image recognition')
    # convertImage('scaled.png', 220)
    print(readNumber('scaled.png', 'nums_2'))
