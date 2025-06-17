import pathlib
import textwrap
import google.generativeai as genai
import os
import gradio as gr
import pymongo
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

def check_exists_mongodb(language_input, cityname_input):
    # Connect to MongoDB and check if data exists
    try:
        uri = os.getenv('MONGODB_URI')

        # Create a new client and connect to the server
        client = MongoClient(uri)
        
        collection = client['TravelAnalysis']['TravelCheckList']
        
        result = collection.find_one({"Language": language_input, "City": cityname_input})

        if result:
            print("Data exists in MongoDB.")
            return result.get("Data")  # Return the "Data" field if found
        else:
            print("No data found in MongoDB.")
            return None
    except Exception as e:
        print(f"Error accessing MongoDB: {e}")
        return None


def save_to_mongodb(language_input,cityname_input,details_input,data):
    # Connect to MongoDB and save the data
    try:
        #uri = "mongodb+srv://tech2hard:Ri7ZdN.z87GMb9.@cluster0.3whtyfc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        uri=os.getenv('MONGODB_URI')
        # Create a new client and connect to the server
        client = MongoClient(uri)                
                
        collection = client['TravelAnalysis']['TravelCheckList']
        
        travelData={"Language":language_input,
                    "City":cityname_input,
                    "Details":details_input,
                    "Data":data}
        
        collection.insert_one(travelData)

    except Exception as e:
        print(f"Error to MongoDB: {e}")


def gemini_chat_builder(language_input,name_input,details_input):
    
    city_data=check_exists_mongodb(language_input,name_input)
    if city_data is not None:
        print("City_data: " + city_data)
    else:
        print("City_data is None")
    if city_data is not None:
        print(f"Data already exists for {language_input} in {name_input}.")
        return city_data
    else:
        if not details_input:
            response=chat.send_message(f"""please create full travel risk analysis of location {name_input}. For clear idea use more info here,{details_input} please provide response in language {language_input}""",generation_config=generation_config)
        else:
            response=chat.send_message(f"""please create full travel risk analysis of location {name_input}. For clear idea use more info here in language {language_input}""",generation_config=generation_config)        
        print(response.text)
        save_to_mongodb(language_input,name_input,details_input,response.text)
        return response.text
    #return f"""The {type_input} is required for the {name_input}"""

API_KEY=os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=API_KEY)

#model=genai.GenerativeModel('gemini-pro')
model=genai.GenerativeModel('gemini-2.0-flash')
generation_config=genai.GenerationConfig(
    stop_sequences=None,
    temperature=0.9,
    top_p=1.0,
    top_k=40,
    candidate_count=1,
    max_output_tokens=2000
)

chat=model.start_chat()

demo=gr.Interface(
    gemini_chat_builder,[
    gr.Dropdown(
        ["English","Spanish","Chinese","Japanese","Korean","Hindi"],multiselect=False,label="Language",info="Select Language",value="English"
    ),
    gr.Textbox(
        label="Input Travel Destination",
        info="Type City or Country",
        lines=1,
        value="Yosemite National Park"
    ),
    gr.Textbox(
        label="Input Details",
        info="Add details to create more meaningful updates",
        lines=1,
        value="Things i should keep in bags"
    )],
    "text",title="Travel Risk Analysis",css="footer {visibility: hidden}",allow_flagging="never",submit_btn=gr.Button("Generate")
)

if __name__=='__main__':
    demo.launch()