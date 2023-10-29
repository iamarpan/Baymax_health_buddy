from typing import Optional
from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
import os
import streamlit as st

class NutritionalValueExtractor:

    def __init__(self):
        self.location = os.environ.get("PROCESSOR_LOCATION")
        self.project_id = os.environ.get("PROJECT_ID")
        self.processor_id = os.environ.get("PROCESSOR_ID")
        self.mime_type = "image/jpeg"  
        opts = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
        self.client = documentai.DocumentProcessorServiceClient(client_options=opts)
        self.name = self.client.processor_path(self.project_id, self.location, self.processor_id)


    def extract_values(self,image_path):
        try:
            streamlit_path = os.path.join('/app/baymax_health_buddy',image_path)
            path = os.path.dirname(__file__)
            my_path = path+'/'+image_path
            st.write("image_apth>>>>",image_path)
            try:
                with open(image_path, "rb") as image:
                    st.write("iamge",image)
                    image_content = image.read()
            except Exception as e:
                st.write("error is >",e)
            raw_document = documentai.RawDocument(content=image_content, mime_type=self.mime_type)
            process_options = documentai.ProcessOptions(
                individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
                    pages=[1]
                )
            )
            try:
                request = documentai.ProcessRequest(
                    name=self.name,
                    raw_document=raw_document,
                    field_mask=None,
                    process_options=process_options,
                )
                result = self.client.process_document(request=request)
            except Exception as e:
                st.write("Error>>>>",e)
            st.write("result",result)
            #document = result.document
            #print("docuemt>>>",document)
            #item_list = {}
            st.write("Cane herere>>>>>>>>>>>>")
            for entity in document.entities:
                item_list[entity.type_]=entity.mention_text
            return item_list
        except:
                print("Error while reading text")


