import os
import cv2
import torch
from google.cloud import vision
import re
import shutil
from PIL import Image
from nutrition_value_extractor import NutritionalValueExtractor  
import streamlit as st
weights_path = 'weights.pt'




class ImageProcessor:

    def __init__(self):
        self.model = torch.hub.load('WongKinYiu/yolov7', 'custom', weights_path, force_reload=True)
        self.nutrientExtractor = NutritionalValueExtractor()

    def process_ingredients(self,ingredients):
        ingredient_list = []    
        for ingredient in ingredients:
            ingredient = ingredient.strip()
            if (ingredient!='') and (not ingredient.startswith("ins")) and (ingredient not in ('.','i','ii','iii','iv','v')) and not re.match(r'\b.*?\d.*?\b', ingredient):
                if ingredient.find("contains") != -1:
                    break
                ingredient_list.append(ingredient)
        return list(set(ingredient_list))

    
    def clean_ingredient_data(self,text):
        text = text.lower()
        ingredients = text.split("ingredients")[1]
        pattern_for_number = r'\d+(\.\d+)?%'
        ingredients = re.sub(pattern_for_number,'',ingredients)
        pattern_for_brackets = r'[{}\[\]():]+'
        ingredients = re.sub(pattern_for_brackets,',',ingredients)
        ingredients = ingredients.replace("and",",")
        ingredients = ingredients.replace("&",',')
        list_of_ingredients = ingredients.split(",")
        return self.process_ingredients(list_of_ingredients)
    

    def extract_nutrients(self,image_path):
        item_list = self.nutrientExtractor.extract_values(image_path)
        print("item_list>>>>>",item_list)
        return item_list


    def get_vision_client(self):
        return vision.ImageAnnotatorClient()

    def extract_ingredients(self,image_path):
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        client = self.get_vision_client()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        ocr_text = response.text_annotations[0].description
        return ocr_text

    def perform_detection_and_cropping(self,image_path,target_size=(640,640)):
        img = cv2.imread(image_path)
        img = cv2.resize(img, target_size)
        results = self.model(image_path)
        print("results>>>>>",results)
        detections = results.xyxy[0].cpu().numpy()
        item_list = ''
        image_text_info = []
        for i, detection in enumerate(detections):
            x1, y1, x2, y2, conf, cls = detection
            cropped_img = cv2.imread(image_path)[int(y1):int(y2), int(x1):int(x2)]
            output_path = os.path.join('static/cropped', f'cropped_{i}.jpg')
            cv2.imwrite(output_path,cropped_img)
            print("cls>>>>>>",cls)
            if cls == 1.0:
                item_list = self.extract_nutrients(output_path)
                        
            elif cls == 0.0:
                image_text = self.extract_ingredients(output_path)
                item_list = self.clean_ingredient_data(image_text)
            else:
                print("No data extracted")
            print("image_text_info>>>>.",image_text_info)
            image_text_info.append((output_path,item_list,cls))
        return image_text_info


if __name__ == '__main__':
    st.title("Baymax Health Buddy!")
    bmi = st.slider('What is your BMI?', 18, 50, 21)
    diabetes = st.radio("Do you have diabetes?",
        ["Yes","No"])
    
    cholestrol = st.radio("Do you have high cholestrol levels?",
        ["Yes","no"])

    uploaded_image = st.file_uploader("Upload an image",type=["jpg","png","jpeg"])

    if uploaded_image is not None:
        st.image(uploaded_image,caption="Uploaded Image",use_column_width=True)
        imageProcessor = ImageProcessor()
        image_text_info=''
        image_path = "temp.jpg"
        with open(image_path, "wb") as f:
            f.write(uploaded_image.read())
    
        try:
            with st.spinner("Hold on Tight... We are extracting information"):
                image_text_info = imageProcessor.perform_detection_and_cropping(image_path)
                for info in image_text_info:
                    if info[2]==1.0:
                        keys = info[1].keys()
                        col1,col2,col3,col4,col5 = st.columns(5)
                        col1.metric("Protein",info[1]['Protein'] if 'Protein' in keys else '')
                        col2.metric("Carbohydrates",info[1]['Carbs'] if 'Carbs' in keys else '')
                        col3.metric("Energy",info[1]['Energy'] if 'Energy' in keys else '')
                        col4.metric("Trans fat",info[1]['Trans_Fat'] if 'Trans_Fat' in keys else '')
                        col5.metric("Saturated Fat",info[1]['Saturated_fat'] if 'Saturated_fat' in keys else '')

                        if(bmi<18.5):
                            st.markdown("- **You are underweight as per your bmi. You should increase your energy intake and also try to have more nutrients in your diet.**")
                        elif(bmi>=18.5 and bmi<25):
                            st.markdown("- **You have the optimum height weight ratio as per your bmi. You should maintain your calorie intake by keeping a track of it.**")
                        elif(bmi>=25 and bmi<=29.9):
                            st.markdown("- **You have the overweight as per your bmi. Try to reduce your fat intake as it may lead to more severe diseases.**")
                        elif(bmi>29.9 and bmi<=34.9):
                            st.markdown("- **You lie in Class I obesity as per your bmi. Reduce your fat and choloestrol intake and exercise to reduce your weight.**")
                        elif(bmi>=35 and bmi<=39.9):
                            st.markdown("- **You lie in Class II obesity as per your bmi. You are at a very high risk of type 2 diabetes and hypertension. Make sure you exercise, reduce your fat and cholestrol intake and include more nutrients and lean food in your diet.**")
                        else:
                            st.markdown("- **You lie in Class III obesity as per your bmi. You are at a extremely high risk of type 2 diabetes and hypertension. Make sure you exercise, reduce your fat and cholestrol intake and include more nutrients and lean food in your diet and consult a medical expert.**")


                        if cholestrol=="Yes":
                            st.markdown("- **Since you have cholestrol make sure to limit your Saturated and Trans fat intake.**")
                        if diabetes=="Yes":
                            st.markdown("- **Since you have diabetes make sure to keep a track of your carbohydrates. Large quantity of carbs can lead to hyperglycemia, which can lead to spike in blood sugar levels.**")
                    else:
                        if len(image_text_info)>1:
                            st.markdown("")
                        else:
                            st.markdown("Unable to extract information. Please upload a clear image")
        except:
            st.markdown("Some Error occured while processing image. Please try again later.")

