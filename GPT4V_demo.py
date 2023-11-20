#%%
import streamlit as st
import graphviz


from dotenv import load_dotenv
from os import environ, getcwd
import toml
import pickle
from pathlib import Path
import time

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
import base64
import requests

from openai import AsyncOpenAI

from dotenv import load_dotenv
from os import environ

import configparser
from py2neo import Relationship

from NEO4J import Neo4jGraph, Now, createNode, createRelation


def get_keys():
    """ Retrieves the keys either from the local file .streamlit/secrets.toml
        for local tests, or from the streamlit sharing secrets manager 
        In the latter case, it's still useful because we test the keys,
        to make sure we're using the ones we think we're using.
    """
    # whether running locally or not, the keys are retreived the same way

    try:
        # let's test is the huggingface token exists
        # ab=st.secrets["secrets"]["HUGGINGFACEHUB_API_TOKEN"]
        # del ab
        assert sum(st.secrets["secrets"]["HUGGINGFACEHUB_API_TOKEN"].encode('ascii')) == 3505, "HuggingFace key is invalid"

        st.write("Keys retrieved!")

        real_code = environ["REAL_CODE"]

        if hash(real_code) != 1232448076957279919:
            del real_code
            st.write('Secret Access code is invalid. Sthg is wrong!')
            st.stop()
        else:
            del real_code

    except:
        st.write('key retrieval issue') 
        st.stop()
    
    # token_id = st.secrets["secrets"]["MODAL_TOKEN_ID"]
    # token_secret = st.secrets["secrets"]["MODAL_TOKEN_SECRET"]
    # openai_api_key = st.secrets["secrets"]["OPENAI_API_KEY"]    
    # assert sum(hf_api_token.encode('ascii')) == 3505, "HuggingFace key is invalid"
    # st.write("HuggingFace key is valid")
    # assert sum(st.secrets["secrets"]["HUGGINGFACEHUB_API_TOKEN"].encode('ascii')) == 3505, "HuggingFace key is invalid"
    # st.write("HuggingFace key is valid")
    # assert sum(token_id.encode('ascii')) == 2207, "Modal token ID is invalid"
    # assert sum(token_secret.encode('ascii')) == 2134, "Modal token secret is invalid"
    # st.write("Modal keys are valid")
    # assert sum(openai_api_key.encode('ascii')) == 4241, "OpenAI key is invalid"
    # st.write("OpenAI key is valid")
    
    return

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
        
# async because of await client.chat.completions.create
async def create_graph( g, 
                        image_path="data/Enjoying-convertible-car.jpg", 
                        plot_image=False, 
                        delete_graph=False,
                        DEBUG=False):

    if plot_image:
        img = mpimg.imread(image_path)
        imgplot = plt.imshow(img)
        plt.show()

    #%%
    # to upload a local image to OpenAI
    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
    }

    prompt = "What’s in this image?"

    def prompt_image(prompt, image_path):
        base64_image = encode_image(image_path)
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
                ]
            }
            ],
            "max_tokens": 300
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            
        return response 

    #%%
    prompt4 = """ 
    Find all objects or people you can find this image and put them in a python list. 
    Be exhaustive, do not miss any object or person, including in the background, the sky if there is one, through a window, behind people, even partially visible etc.
    Just list one object at a time, do not include what they are doing or where they are, just the object / person name only.
    For instance, "women wearing hats" is two objects "women" and "hats"
    """
    ans4 = prompt_image(prompt4, image_path)
    objects_in_image = ans4.json()["choices"][0]["message"]["content"].split("\n")
    if DEBUG:
        st.write("Objects in image:")
        st.write(ans4.json()["choices"][0]["message"]["content"])

    #%%
    prompt3 = """ 
    list all possible beliefs we can extract from this image, and express them in this format
    <this thing or person> <action> <another thing><for this reason or purpose><in these conditions ><optional>... 
    Please keep the propositions with the <action> to leave <another thing> as an object/person name

    You can also use another format, when there is no action, using the verb 'to be', such as:
    <this car><is><a convertible><because the roof can be removed>

    To generate all possible beliefs, in an exhaustive way, look at all the objects, persons, background etc and try to find a relation between them following the formats above.
    Do not output anything before the first '<' and after the last '>'.
    Do not output the '<' or '>' characters.
    """
    ans3 = prompt_image(prompt3, image_path)
    if DEBUG:
        st.write(ans3.json()["choices"][0]["message"]["content"])
    #%%
    beliefs = [f"belief{i}: "+ans for i,ans in enumerate(ans3.json()["choices"][0]["message"]["content"].split("\n"), 1)]
    if DEBUG:
        st.write('\n'.join(beliefs))
    #%%
    instructPrompt = """
    You are an expert in linguistics, semantic and you are trying to format the beliefs passed to you into a format that can be stored in a knowledge graph.
    The beliefs start with the word 'belief1:', 'belief2:' etc and are separated by a new line.

    Rewrite every belief and express them as a python dictionary with the following format:
    {
        "condition": <conditions observed from the picture such as a sunny day, ie the conditions leading to the rest of the beliefs, such as the objective and action>,
        "objective": <the objective of the person or thing in the picture, after observing the conditions in the picture>,
        "subject": <the person or thing in the picture doing the 'action' to meet the 'objective', just one word if possible>,
        "action": <the action the person or thing in the picture is doing to meet the 'objective', expressed in one word with an optional preposition, such as 'drive to'>,
        "object": <the object of the action, expressed in one word if possible such as 'beach', NOT 'the beach'>
    }
    Use an empty string when a field is not available.
    Do not return a belief if the subject and actions are not clearly identified.

    I want general answers, not specific to an image.
    For instance, I would expect something like:
    {
        "condition": "sunny day",
        "objective": "enjoy the countryside",
        "subject": "people",
        "action": "drive",
        "object": "convertible"
    }
    not the following
    {
        "condition": "in a sunny day",
        "objective": "because he enjoys the countryside",
        "subject": "the person in the driver seat",
        "action": "drive",
        "object": "the convertible"
    }
    For "subject", "action", "object", be as generic and short as possible.

    When the belief does not have an action, but instead use a verb such as 'to be' for instance, then put the verb in the <action anyway>, 
    and use the field 'object' to describe what the object or person is or is made of or anything else that the verb describes.

    Use infinitive verbs, without the 'to', ie 'be' instead of 'is'.  
    """
    #%%  BUILD INSTRUCT PROMPT AND GO!
    # NO CHUNKING, THE PROMPT IS SHORT ENOUGH
    requestMessages = [instructPrompt + '\n' + belief for belief in beliefs]
    
    # async def getCompletion(requestMessages):
    chatOutputs = []
    for request in requestMessages:  
        chatOutput = await client.chat.completions.create(
                    model="gpt-4",  # previous models, even GPT3.5 didn't work that well
                    messages=[{"role": "system", "content": "You are an expert in linguistics, semantic"},
                            {"role": "user", "content": request} ]
        )
    chatOutputs.append(chatOutput)
    # return chatOutputs
    
    # chatOutputs = getCompletion(requestMessages)
    #%%
    formatted_beliefs = {}
    for belief in chatOutputs:
        b = json.loads(belief.choices[0].message.content)
        formatted_beliefs[b["subject"]] = b
        if DEBUG:
            st.write(b)

    #%%
    if delete_graph:
        g.deleteAllNodes(DEBUG=True)
        assert g.nodesNb == 0
        if DEBUG:
            st.write("Graph has been cleaned")

    for b in chatOutputs:
    
        belief = json.loads(b.choices[0].message.content)
        
        name=belief.pop("subject")
        object = belief.pop("object")
        relation = belief.pop("action")
        if DEBUG:
            st.write('\n'.join([name, relation, object, belief['objective'], belief['condition']]))
        
        try:
            subject1  = createNode(g, name,
                                user_id='JPB',
                                display_name=name,
                                labels_constraints=name,  # we don't create the same object/subject twice
                                # properties_constraints=('user_id',), 
                                creation_timestamp = Now(),
                                DEBUG=True)  # we can have the same subject appear several times
            
        except:
            if DEBUG:
                st.write(f"node not created for {name}")
        
        try:
            object1  = createNode(g, object,
                                user_id='JPB',
                                display_name=object,
                                labels_constraints=object,  
                                properties_constraints=('user_id',), 
                                creation_timestamp = Now(),
                                DEBUG=True,
                                **belief,
                                )
        except:
            if DEBUG:
                st.write(f"node not created for {object}")
            
        try:
            relat1 = createRelation(g, subject1, 
                                    object1, 
                                    relation,
                                    DEBUG=True,
                                    #synonyms='has imagery',  # for demo, relations can have properties as well
                                    allow_duplicates=True,   # Neo4J allows several identical relations between 2 nodes, but we don't want that
                                    counting=True)
        except:
            if DEBUG:
                st.write(f"relation not created for 'to {relation}'")
            
        if DEBUG:
            st.write("="*50)
        
    if DEBUG:
        st.write("Nb of nodes =", g.nodesNb)

    return objects_in_image, beliefs

def main():
    st.image('images/banner.png', use_column_width=True)
    st.title("Team NoLimits")

    codebox = st.empty()
    code = codebox.text_input("Enter your access code here", 
                                value="", 
                                placeholder="........",
                                key="1")


    get_keys()

    # ok, we can start the GPU
    graph_data2 = run_on_GPU(modelname="tiiuae/falcon-7b-instruct", 
                            prompt=make_prompt(), 
                            animals=['cat', 'elephant'])
    st.write("Features are found")

    # graph_data2 = {"cat": "tail, 4 legs, body, 2 eyes, nose, 2 ears, a mouth, whiskers".split(', '),
    #             "dog": "tail, 4 legs, body, 2 eyes, nose, 2 ears, a mouth, tongue".split(', '),}

    plot_graph(graph_data2, msg="Features graphs extracted by Falcon 7B Instruct")

    # pickle the data only when running locally
    if Path("/data/pickle files/").exists:
        for animal, features in graph_data2.items():
            #st.write(f'Features of {animal} are', features)
            update_pickle({animal:features}, "features")




if __name__ == '__main__':

    # I setup a free Neo4J instance on Aura, and I'm using the Python driver to connect to it

    Neo4j_config = configparser.ConfigParser()
    Neo4j_config.read('neo4j_config.ini')
    Neo4j_config['DEFAULT']["pw"] = environ['NEO4J_AURA_PW']

    g = Neo4jGraph(showstatus=True, **Neo4j_config['DEFAULT'])

    # in case of error, check your config.ini file

    # Instructions to see the graph in Neo4J Browser
    # go to 
    # https://workspace-preview.neo4j.io/workspace/query?ntid=auth0%7C631bb4216f68981ab949290b
    # run the cypher query: 
    # MATCH (n) RETURN n     to see all nodes
    
    
    g.deleteAllNodes(DEBUG=True)
    assert g.nodesNb == 0
    st.write("Graph has been cleaned")

    import asyncio
    objects_in_image, beliefs = asyncio.run(create_graph(g, 
                                            image_path="data/Enjoying-convertible-car.jpg", 
                                            plot_image=True,
                                            delete_graph=True,
                                            DEBUG=True
    ))
    st.write('\n'.join(beliefs))

    main()

# get into venv and run 
#    streamlit run src/frontend/frontend.py --server.allowRunOnSave True
# we must run it from the root folder, not from the src folder because 
# that's what streamlit will do