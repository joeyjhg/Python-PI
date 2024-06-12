import cv2


##이미지를 받아서 화폐 인지 아닌지 검사
##결과가 True 라면 True를 리턴 및 이미지 저장
def userCertify_filesave(image, money_process_filename):
    img_copy = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    img_dilate = cv2.dilate(gray, kernel)
    img_erode = cv2.erode(img_dilate, kernel)
    img_blur = cv2.GaussianBlur(img_erode, (3, 3), 0)
    img_binary = cv2.adaptiveThreshold(
        img_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )
    img_contrast = cv2.equalizeHist(img_binary)
    img_processed = cv2.subtract(255, img_contrast)

    img_close = cv2.morphologyEx(img_processed, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(img_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    maxArea = 0
    contour = None
    check = False

    for pts in contours:
        area = cv2.contourArea(pts)

        if area > maxArea:
            maxArea = area
            contour = pts
            check = True

    if check:
        (x, y, w, h) = cv2.boundingRect(contour)

        if (w >= 100 and h >= 100) and (w <= 600 and h <= 600):
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)

            for i in range(0, 2, 1):
                url = "static/money/"
                if i == 0:
                    url += "1000won.jpg"
                elif i == 1:
                    url += "10000won.jpg"

                targetImage = image[y : y + h, x : x + w]
                standardImage = cv2.imread(url, cv2.IMREAD_ANYCOLOR)
                final_score = compareFeature(targetImage, standardImage)

                print("Similarity(일치율) : " + str(final_score) + " % ")
                if final_score >= 60:
                    if i == 0:
                        print("\n천원 입니다")
                    elif i == 1:
                        print("\n만원 입니다")
                    cv2.imwrite(money_process_filename, image)
                    return True

            print("검출 실패")
            cv2.imwrite(money_process_filename, img_copy)
            return False
    else:
        print("컨투어 검출 실패")
        cv2.imwrite(money_process_filename, img_copy)
        return False


def userCertify(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    img_dilate = cv2.dilate(gray, kernel)
    img_erode = cv2.erode(img_dilate, kernel)
    img_blur = cv2.GaussianBlur(img_erode, (3, 3), 0)
    img_binary = cv2.adaptiveThreshold(
        img_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )
    img_contrast = cv2.equalizeHist(img_binary)
    img_processed = cv2.subtract(255, img_contrast)

    img_close = cv2.morphologyEx(img_processed, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(img_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    maxArea = 0
    contour = None
    check = False

    for pts in contours:
        area = cv2.contourArea(pts)

        if area > maxArea:
            maxArea = area
            contour = pts
            check = True

    if check:
        (x, y, w, h) = cv2.boundingRect(contour)

        if (w >= 100 and h >= 100) and (w <= 600 and h <= 600):
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)

            for i in range(0, 2, 1):
                url = "static/money/"
                if i == 0:
                    url += "1000won.jpg"
                elif i == 1:
                    url += "10000won.jpg"

                targetImage = image[y : y + h, x : x + w]
                standardImage = cv2.imread(url, cv2.IMREAD_ANYCOLOR)
                final_score = compareFeature(targetImage, standardImage)

                print("Similarity(일치율) : " + str(final_score) + " % ")
                if final_score >= 60:
                    if i == 0:
                        print("\n천원 입니다")
                    elif i == 1:
                        print("\n만원 입니다")
                    # cv2.imwrite(money_process_filename, image)
                    return True

            print("검출 실패")
            # cv2.imwrite(money_process_filename, image)
            return False
    else:
        print("컨투어 검출 실패")
        # cv2.imwrite(money_process_filename, image)
        return False


##ORB 알고리즘을 이용한 일치율 확인
def compareFeature(img1, img2):

    retVal = 0
    startTime = cv2.getTickCount()
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2, None)

    # matches = matcher.match(descriptors1, descriptors2)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    max_dist = 0
    min_dist = 100
    try:
        for match in matches:
            dist = match.distance
            if dist < min_dist:
                min_dist = dist
            if dist > max_dist:
                max_dist = dist

        print("\n/////////////////////////////////////////")
        print("키포인트 개수=", len(matches))
        print("max_dist=", max_dist, ", min_dist=", min_dist)

        for match in matches:
            if match.distance <= 50:
                retVal += 1

        print("매칭 개수=", retVal)
        estimatedTime = int(
            (cv2.getTickCount() - startTime) / cv2.getTickFrequency() * 1000
        )
        print("소요 시간=", estimatedTime, "ms")

        return (retVal / len(matches)) * 100
    except Exception:
        return 0


## test code ##
# if __name__ == "__main__":
#     image = cv2.imread("img/pic.jpg", cv2.IMREAD_ANYCOLOR)
#     userCertify(image)
