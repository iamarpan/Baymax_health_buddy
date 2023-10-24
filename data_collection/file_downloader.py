import pandas as pd
import requests
import os
from io import BytesIO
from PIL import Image
from tqdm import tqdm

df = pd.read_csv('links2.csv',header=None)  # Replace with your DataFrame source
download_folder = 'image_downloads2'
os.makedirs(download_folder, exist_ok=True)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}


for index, row in tqdm(df.iterrows()):
    image_url = row[0]
    try:
        response = requests.get(image_url,headers=headers)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image_path = os.path.join(download_folder, f'image_{index}.jpg')
            image.save(image_path)
#            print(f'Downloaded: {image_url}')
        else:
            print(f'Failed to download: {image_url}')
    except Exception as e:
        print(f'Error while downloading {image_url}: {e}')

