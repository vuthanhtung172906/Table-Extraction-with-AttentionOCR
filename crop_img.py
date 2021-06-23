import cv2
import numpy as np
import imutils


def biggestCnt(contours):
    biggest = np.array([])
    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 5000:
            approx = cv2.approxPolyDP(cnt, 0.02*cv2.arcLength(cnt, True), True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest, max_area


def getLengthWidth(biggest):
    width = ((biggest[0][0][0] - biggest[1][0][0])**2 +
             (biggest[0][0][1]-biggest[1][0][1])**2)**0.5
    length = ((biggest[0][0][0] - biggest[2][0][0])**2 +
              (biggest[0][0][1]-biggest[2][0][1])**2)**0.5
    return length, width


def drawRectangle(img, biggest, thickness):
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]),
             (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]),
             (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]),
             (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]),
             (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    return img


def reorder(biggest):
    myPoints = biggest.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
    add = myPoints.sum(1)
    myPointsNew[0] = myPoints[np.argmin(add)] + [[-5, -5]]
    myPointsNew[3] = myPoints[np.argmax(add)] + [[5, 5]]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)] + [[5, -5]]
    myPointsNew[2] = myPoints[np.argmax(diff)] + [[-5, 5]]
    return myPointsNew


def crop_imgFunc(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)

    thres = [200, 255]
    imgThreshold = cv2.Canny(imgBlur, thres[0], thres[1])
    kernel = np.ones((5, 5))
    imgDial = cv2.dilate(imgThreshold, kernel, iterations=2)  # APPLY DILATION
    imgThreshold = cv2.erode(imgDial, kernel, iterations=2)  # APPLY EROSION
    # FIND BIGGEST COUNTOUR
    contours, hierarchy = cv2.findContours(
        imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    biggest, max_area = biggestCnt(contours)
    biggest = reorder(biggest)
    # Warp
    length, width = getLengthWidth(biggest)
    pts1 = np.float32(biggest)
    pts2 = np.float32([[0, 0], [width, 0], [0, length], [width, length]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarpColored = cv2.warpPerspective(
        img, matrix, (int(width), int(length)))
    imgFinal = imgWarpColored[:, 0:842]
    return imgFinal
