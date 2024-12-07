
import base64
from io import BytesIO
import json
import os
import time
from uuid import uuid4
from PyPDF2 import PdfReader
from duckduckgo_search import DDGS
from fastapi import HTTPException
from langchain_core.messages import BaseMessage
from agents.constants.ai_models import chat_json
from agents.constants.prompts import ALTER_MERMAID_GENERATION_SYSTEM_PROMPT, ANALYZE_MERMAID_GENERATION_SYSTEM_PROMPT, MERMAID_GENERATION_SYSTEM_PROMPT, QUERY_GENERATION_SYSTEM_PROMPT
from agents.utils.blogs import addBlogPost


def start_workflow(state):
    return {
        "messages": [
            BaseMessage(content="Hey, I'm Rhea, your nerdy AI Web3 Researcher. The mermaid diagram, Logan made along with you've is nice, let me see how I can help you get your business onchain",
                        role="system", type="text",name="Rhea")
        ]
    }

def process_input(state):
    messages = state["messages"]
    user_input = messages[-1]
    return {
        "messages": messages,
        "mermaid_input": user_input.content,
    }

def usecase_generator(state):
    mermaid_input = state['mermaid_input']
    try:
        response = chat_json.invoke(
            [
                {"role": "system", "content": ANALYZE_MERMAID_GENERATION_SYSTEM_PROMPT},
                {"role": "human", "content": mermaid_input}
            ]
        )
        content = response.content
        if not content:
            raise HTTPException(
                status_code=500, detail="Failed to extract style details")

        # Parse JSON response
        try:
            res = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to parse JSON: {str(e)}")
    except Exception as e:
        raise ValueError("Failed to generate queries from the user prompt.")
    return {
        "messages": [
            BaseMessage(content="Here are some usecases I think you might want to get onchain for",
                        role="system", type="options", name="Rhea")
        ],
        "options": res.get("ways", "")
    }

def usecase_buffer(state):
    messages = state["messages"]
    user_input = messages[-1]

    if user_input.content.lower() == "no":
        return {
            "messages": [
                BaseMessage(content="Oki leme see what else I can think of if you dont like any of these. Select the one you like.", type= "text", role="system", name="Rhea")
            ],
        }
    else:
        mermaid_input = state.get('mermaid_input') 
        options = state.get("options")
        if not mermaid_input:
            raise HTTPException(status_code=400, detail="Mermaid input is required")

        try:
            # Invoke the chat system with the Mermaid input
            response = chat_json.invoke(
                [
                    {"role": "system", "content": ALTER_MERMAID_GENERATION_SYSTEM_PROMPT},
                    {"role": "human", "content": json.dumps(options[int(user_input.content)]), "type": "text"},
                    {"role": "human", "content": json.dumps(mermaid_input), "type": "text"}
                ]
            )

            # Check if response content exists
            content = response.content
            if not content:
                raise HTTPException(
                    status_code=500, detail="Failed to extract style details"
                )

            # Parse JSON response
            try:
                res = json.loads(content)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=500, detail=f"Failed to parse JSON: {str(e)}"
                )

        except Exception as e:  # Catch all other exceptions
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred: {str(e)}"
            )
        
        altered_image = res.get("mermaid_diagram_string")
        addBlogPost(options[int(user_input.content)],altered_image)




        return {
            "messages": [
                BaseMessage(content="Nice, good choice! you should continue to talk to Kanye now to figure out how you can embed this, he's our tech guy!", type= "moveToCoder", role="system", name="Rhea")
            ],
            "altered_mermaid": altered_image,
            "output": options[int(user_input.content)], 
            "finished": True
        }



def end_workflow(state):
    return state

# Edges

def usecase_modifier(state):
    finished = state["finished"]
    
    if finished == True:
        return "end"
    else: 
        return "process_input"
