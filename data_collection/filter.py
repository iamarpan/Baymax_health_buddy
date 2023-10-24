import os
import shutil
import pytesseract
from PIL import Image
import cv2
from tqdm import tqdm

def check_image(image_path):
    try:
        image = cv2.imread(image_path)
        resized_image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
        blur_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
        thresholded_image = cv2.threshold(blur_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        pillow_image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))

        result = pytesseract.image_to_string(pillow_image)
        if "nutritional" in result.lower():
            return True
        return False

    except:
        print("Error while reading file:",image_path)
        return False


def read_files():
    source_folder = "./image_downloads2"
    destination_folder = "./nutritional_value"

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    file_list = os.listdir(source_folder)

    for file_name in tqdm(file_list):
        source_file_path = os.path.join(source_folder, file_name)
        destination_file_path = os.path.join(destination_folder, file_name)
        response = check_image(source_file_path)
        if response:
            print("copying file:{0}".format(source_file_path))
            shutil.copy2(source_file_path, destination_file_path)

    print("Files copied successfully.")


if __name__ == '__main__':
    read_files()
