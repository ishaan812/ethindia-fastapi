
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
from agents.constants.prompts import ANALYZE_MERMAID_GENERATION_SYSTEM_PROMPT, MERMAID_GENERATION_SYSTEM_PROMPT, QUERY_GENERATION_SYSTEM_PROMPT


def start_workflow(state):
    return {
        "messages": [
            BaseMessage(content="Hey, I'm Alex, your AI Web3 Researcher. The mermaid diagram you've made is nice, let me see how I can help you get your business onchain",
                        role="system", type="text")
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
                        role="system", type="text")
        ],
        "options": res.get("ways", "")
    }

def usecase_buffer(state):
    messages = state["messages"]
    user_input = messages[-1]

    if user_input.content.lower() == "no":
        return {
            "messages": [
                BaseMessage(content="Oki leme see what else I can think of if you dont like any of these", type= "text", role="system")
            ],
        }
    else:
        return {
            "messages": [
                BaseMessage(content="Nice, you should talk to Kanye now to figure out how you can embed this, he's our tech guy!", type= "text", role="system")
            ],
            "finished": True,
        }



def end_workflow(state):
    return {
        "messages": [
            BaseMessage(content="Thanks! Its been a pleasure working with you, you can now talk to my colleague Kanye",
                        role="system", type="text")
        ]
    }

# Edges

def usecase_modifier(state):
    finished = state["finished"]
    
    if finished == True:
        return "end"
    else: 
        return "process_input"