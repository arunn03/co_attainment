from django.contrib.staticfiles import finders

import cv2
import numpy as np
import tensorflow as tf

def threshold_img(image):
    ret, thresh = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY_INV)
    return thresh


def rotate_img(image):
    angle = -20

    center = (image.shape[1] // 2, image.shape[0] // 2)

    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]),
                                   flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

    return rotated_image

def recognize_marks(answer_script):
    mask_path = finders.find('assets/mask.jpg')
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    # answer_script = cv2.imread(answer_script, cv2.IMREAD_GRAYSCALE)

    # Extracting the mark regions
    kernel = np.ones((3, 5), np.uint8)
    inner_mask = cv2.erode(mask, kernel, iterations=10)
    final_masked_image = cv2.bitwise_and(answer_script, answer_script, mask=inner_mask)

    # Applying threshold on whole answer script
    thresh_img = threshold_img(final_masked_image)
    thresh_img = cv2.bitwise_or(thresh_img, thresh_img, mask=inner_mask)

    # Dilating the mask image for accessing each rows
    kernel = np.ones((1, 110), np.uint8)
    dilated_img = cv2.dilate(inner_mask, kernel, iterations=1)

    # Finding contours from dilated mask image
    contours, heirarchy = cv2.findContours(dilated_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sorted_contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
    sorted_contours = np.array(list(filter(lambda c: cv2.contourArea(c) >= 10000, sorted_contours)), dtype=object)

    # MNIST digit recognizing deep learning model
    model_path = finders.find('assets/digit_recognizer.keras')
    model = tf.keras.models.load_model(model_path)

    img3 = answer_script.copy()
    marks = {}
    questions = (
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
        '11a', '12a', '13a', '14a', '15a', '16a', '17a', '18a',
        '11b', '12b', '13b', '14b', '15b', '16b', '17b', '18b',
        '11c', '12c', '13c', '14c', '15c', '16c', '17c', '18c',
    )
    question_ind = 0

    # Traversing each row
    for c in sorted_contours:
        x, y, w, h = cv2.boundingRect(c)
        roi_line = dilated_img[y:y + h, x:x + w]
        line_mask = final_masked_image[y:y + h, x:x + w]

        line_img = cv2.bitwise_and(roi_line, roi_line, mask=line_mask)

        cnt, hr = cv2.findContours(line_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        sorted_contour_words = sorted(cnt, key=lambda c: cv2.boundingRect(c)[0])
        sorted_contour_words = list(filter(lambda c: cv2.contourArea(c) >= 500, sorted_contour_words))

        # Traversing each number
        for word in sorted_contour_words:
            x2, y2, w2, h2 = cv2.boundingRect(word)
            num_img = img3[y + y2:y + y2 + h2, x + x2:x + x2 + w2]
            num_kernel = np.ones((5, 5), np.uint8)
            thresh_num_img = threshold_img(num_img)
            dilated_num_img = cv2.dilate(thresh_num_img, num_kernel, iterations=1)

            digit_cnt, digit_hr = cv2.findContours(dilated_num_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            sorted_contour_digits = sorted(digit_cnt, key=lambda c: cv2.boundingRect(c)[0])
            filtered_contour_digits = list(filter(lambda c: cv2.contourArea(c) >= 100, sorted_contour_digits))
            number = None

            if len(filtered_contour_digits) == 0:
                number = 0

            # Traversing each digit
            for digit in filtered_contour_digits:
                x3, y3, w3, h3 = cv2.boundingRect(digit)

                digit_img = img3[y + y2 + y3:y + y2 + y3 + h3, x + x2 + x3:x + x2 + x3 + w3]
                digit_img = threshold_img(digit_img)
                digit_img = cv2.copyMakeBorder(digit_img, 24, 24, 24, 24, cv2.BORDER_CONSTANT)
                digit_img = cv2.resize(digit_img, (28, 28), interpolation=cv2.INTER_AREA)
                digit_img = rotate_img(digit_img)

                prediction = model.predict(np.array([digit_img]))
                digit = np.argmax(prediction)
                if number is None:
                    number = 0
                number = number * 10 + digit  # Combining the predicted digits into a single

            if number is not None:
                marks[questions[question_ind]] = number
                question_ind += 1

    del model
    tf.keras.backend.clear_session()
    
    # x, y, w, h = 192, 1912, 2264, 1440
    # answer_script = answer_script[y:y+h, x:x+w, :]
    # answer_script = cv2.cvtColor(answer_script, cv2.COLOR_BGR2RGB)

    # desired_height = 300
    # ratio = desired_height / answer_script.shape[0]
    # new_dimensions = (int(answer_script.shape[1] * ratio), desired_height)
    # answer_script = cv2.resize(answer_script, new_dimensions, interpolation=cv2.INTER_AREA)

    # return marks, answer_script

    return marks