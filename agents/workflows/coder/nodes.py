
import json
from fastapi import HTTPException
from langchain_core.messages import BaseMessage
from agents.constants.ai_models import chat_json
from agents.constants.prompts import PLAN_SMART_CONTRACT_CREATION, SOLIDITY_CODE_GENERATION_SYSTEM_PROMPT


def start_workflow(state):
    return {
        "messages": [
            BaseMessage(content="Yo, I'm Kanye, I’m the blockchain Yeezy, contracts stay breezy—code so tight, even bugs get queasy. Let's get started on your project.",
                        role="system", type="text")
        ]
    }

def process_input(state):
    messages = state['messages']
    user_input = messages[-1]
    return {"usecase": json.loads(user_input.content)}


def plan_smart_contract(state):
    usecase = state['usecase']
    plan_messages = state.get("plan_messages", [])
    plan = state.get("plan", "")
    if len(plan_messages) == 0:
        plan_messages = [
            {"role": "system", "content": PLAN_SMART_CONTRACT_CREATION },
            {"role": "human", "content": "Usecase: " + json.dumps(usecase)}
        ]
    else:
        messages = state['messages']
        user_input = messages[-1]
        plan_messages.append({"role": "system", "content": json.dumps(plan), "type": "text"})
        plan_messages.append({"role": "human", "content": user_input.content, "type": "text"})


    try:
        response = chat_json.invoke(plan_messages)
        content = response.content
        if not content:
            raise HTTPException(
                status_code=500, detail="Failed to extract style details")

        try:
            res = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to parse JSON: {str(e)}")
    except Exception as e:
        raise ValueError("Failed to generate plan.")
    return {
        "messages": [
            BaseMessage(content="Yo, here’s the plan for the smart contract, let me know if it’s fire or if we need to tweak it. You got thoughts, throw ‘em in. Let’s make this legendary. Type continue to proceed.",
                        role="system", type="text"),
            BaseMessage(content=json.dumps(res.get("plan", "")), role="system", type="default")
        ],
        "plan": res.get("plan", ""),
        "plan_messages": plan_messages
    }


def code_node(state):
    messages = state['messages']
    user_input = messages[-1]
    generated_code = state.get("generated_code", "")
    final_plan = state["plan"]
    code_messages = state.get("code_messages", [])
    if len(code_messages) == 0:
        code_messages = [
            {"role": "system", "content": SOLIDITY_CODE_GENERATION_SYSTEM_PROMPT},
            {"role": "human", "content": "Final Plan: " + json.dumps(final_plan)}
        ]
    else:
        messages = state['messages']
        user_input = messages[-1]
        code_messages.append({"role": "system", "content": json.dumps(generated_code)})
        code_messages.append({"role": "human", "content": user_input.content})

    try:
        response = chat_json.invoke(code_messages)
        content = response.content
        if not content:
            raise HTTPException(
                status_code=500, detail="Failed to generate code.")

        try:
            res = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to parse JSON: {str(e)}")
    except Exception as e:
        raise ValueError("Failed to generate queries from the user prompt.")
    return {
        "messages": [
            BaseMessage(content="Yo, here’s the code, let me know if it’s fire or if we need to tweak it. You got thoughts, throw ‘em in. Let’s make this legendary. Type ``continue`` to deploy it on the chain.",
                        role="system", type="text"),
        ],
        "generated_code": res.get('code', ''),
        "code_messages": code_messages
    }    

def deploy_smart_contract(state):
    pass

def get_feedback(state):
    pass

def end_workflow(state):
    pass

# Edges

def plan_approval_modifier(state):
    messages = state['messages']
    user_input = messages[-1]
    if "continue" in user_input.content.lower():
        return "code_node"
    else:
        return "plan_smart_contract"

def code_approval_modifier(state):
    messages = state['messages']
    user_input = messages[-1]
    if "continue" in user_input.content.lower():
        return "deploy_smart_contract"
    else:
        return "code_node"
