import cv2
from PIL import Image, ImageEnhance
import numpy as np
from matplotlib import pyplot as plt
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from craft_text_detector import Craft

import crop_img2


def group_h_lines(h_lines, thin_thresh):
    new_h_lines = []
    while len(h_lines) > 0:
        thresh = sorted(h_lines, key=lambda x: x[0][1])[0][0]
        lines = [line for line in h_lines if thresh[1] -
                 thin_thresh <= line[0][1] <= thresh[1] + thin_thresh]
        h_lines = [line for line in h_lines if thresh[1] - thin_thresh >
                   line[0][1] or line[0][1] > thresh[1] + thin_thresh]
        x = []
        for line in lines:
            x.append(line[0][0])
            x.append(line[0][2])
        x_min, x_max = min(x) - int(5*thin_thresh), max(x) + int(5*thin_thresh)
        new_h_lines.append([x_min, thresh[1], x_max, thresh[1]])
    return new_h_lines


def group_v_lines(v_lines, thin_thresh, img):
    new_v_lines = []
    while len(v_lines) > 0:
        thresh = sorted(v_lines, key=lambda x: x[0][0])[0][0]
        lines = [line for line in v_lines if thresh[0] -
                 thin_thresh <= line[0][0] <= thresh[0] + thin_thresh]
        v_lines = [line for line in v_lines if thresh[0] - thin_thresh >
                   line[0][0] or line[0][0] > thresh[0] + thin_thresh]
        y = []
        for line in lines:
            y.append(line[0][1])
            y.append(line[0][3])
        y_min, y_max = min(y) - int(4*thin_thresh), max(y) + int(4*thin_thresh)
        if y_max-y_min >= img.shape[0]-10:
            new_v_lines.append([thresh[0], y_min, thresh[0], y_max])
    return new_v_lines


def processImg(img):
    img = crop_img2.crop_imgFunc(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh, img_bin = cv2.threshold(
        gray, 90, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    img_bin = 255-img_bin
    kernel_len = gray.shape[1]//120
    hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
    image_horizontal = cv2.erode(img_bin, hor_kernel, iterations=3)
    horizontal_lines = cv2.dilate(image_horizontal, hor_kernel, iterations=3)
    h_lines = cv2.HoughLinesP(
        horizontal_lines, 1, np.pi/180, 100, maxLineGap=250)

    new_horizontal_lines = group_h_lines(h_lines, kernel_len)
    for i in range(len(new_horizontal_lines)):
        cv2.line(img, (new_horizontal_lines[i][0], new_horizontal_lines[i][1]), (
            new_horizontal_lines[i][2], new_horizontal_lines[i][3]), (0, 255, 0), 1)

    kernel_len = gray.shape[1]//120
    ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
    image_vertical = cv2.erode(img_bin, ver_kernel, iterations=3)
    vertical_lines = cv2.dilate(image_vertical, ver_kernel, iterations=3)
    v_lines = cv2.HoughLinesP(vertical_lines, 1, np.pi/180, 30, maxLineGap=250)
    new_vertical_lines = group_v_lines(v_lines, kernel_len, img)
    for i in range(len(new_vertical_lines)):
        cv2.line(img, (new_vertical_lines[i][0], new_vertical_lines[i][1]), (
            new_vertical_lines[i][2], new_vertical_lines[i][3]), (0, 255, 0), 1)

    def seg_intersect(line1: list, line2: list):
        a1, a2 = line1
        b1, b2 = line2
        da = a2-a1
        db = b2-b1
        dp = a1-b1

        def perp(a):
            b = np.empty_like(a)
            b[0] = -a[1]
            b[1] = a[0]
            return b

        dap = perp(da)
        denom = np.dot(dap, db)
        num = np.dot(dap, dp)
        return (num / denom.astype(float))*db + b1
    points = []
    for hline in new_horizontal_lines:
        x1A, y1A, x2A, y2A = hline
        for vline in new_vertical_lines:
            x1B, y1B, x2B, y2B = vline

            line1 = [np.array([x1A, y1A]), np.array([x2A, y2A])]
            line2 = [np.array([x1B, y1B]), np.array([x2B, y2B])]

            x, y = seg_intersect(line1, line2)
            if x1A <= x <= x2A and y1B <= y <= y2B:
                points.append([int(x), int(y)])
    cells = []
    for i in range(len(points)):
        if (i+1) % 6 == 0:
            continue
        if (i+6) == len(points):
            break

        cells.append([points[i], points[i+1], points[i+6], points[i+7]])
    return cells, img


def load_model():
    # & VietOCR
    # set device to use cpu
    config1 = Cfg.load_config_from_name('vgg_seq2seq')
    config2 = Cfg.load_config_from_file('config.yml')
    config1['cnn']['pretrained'] = False
    config2['cnn']['pretrained'] = False
    config2['weights'] = './weights/transformerocr.pth'
    detector2 = Predictor(config2)
    detector1 = Predictor(config1)
    craft = Craft(crop_type="box", cuda=True)
    return detector1, detector2, craft


def predict(img, detector1, detector2):
    cells, img = processImg(img)
    result2 = []
    for id, cell in enumerate(cells):
        if id > 5 and (id+1) % 5 == 0:
            x_min = cell[0][0]  # Top
            x_max = cell[3][0]  # Right
            y_min = cell[0][1]
            y_max = cell[3][1] + 10
            cell_image = img[y_min:y_max, x_min:x_max]
            img_text = Image.fromarray(cell_image)
            result = detector2.predict(img_text)
            result2.append(result)
        else:
            x_min = cell[0][0]  # Top
            x_max = cell[3][0]  # Right
            y_min = cell[0][1]
            y_max = cell[3][1]
            cell_image = img[y_min:y_max, x_min:x_max]
            img_text = Image.fromarray(cell_image)
            # # # predict
            result = detector1.predict(img_text)
            result2.append(result)
    result = []
    for i in range(0, len(result2), 5):
        result.append([result2[i], result2[i+1], result2[i+2],
                       result2[i+3], result2[i+4]])
    return result
