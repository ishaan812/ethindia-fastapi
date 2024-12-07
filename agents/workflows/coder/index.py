import json
import os
from typing import Annotated, List, Literal, Optional, TypedDict
from fastapi import HTTPException
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from agents.utils.helpers import stripped_uuid4
from agents.workflows.index import WorkflowInterface
from operator import add
from agents.workflows.coder.nodes import code_approval_modifier, code_node, deploy_smart_contract, end_workflow, get_feedback, plan_approval_modifier, plan_smart_contract, start_workflow, process_input
from agents.constants.cdp import fetch_wallet

class WorkflowState(TypedDict):
    wallet_id: str
    messages: Annotated[list, add_messages]
    usecase: str
    feature_list: list[str]
    plan_messages: List
    code_messages: List
    generated_code: str
    plan: dict
    token_name: str
    token_abbreviation: str
    contract_address: str


class CoderWorkflow(WorkflowInterface):
    def __init__(self, Checkpointer):
        self.wallet_id = "ef94618f-89c7-4123-bb87-684cb712a99b"
        self.graph = StateGraph(WorkflowState)
        self._initialize_graph()
        self.workflow_instance = self.graph.compile(
            interrupt_after=["start", "plan_smart_contract", "code_node", "get_feedback"],
            checkpointer=Checkpointer,
        )

    def _initialize_graph(self):
        """Setup the state graph for the workflow process."""
        self.graph.add_node('start', start_workflow)
        self.graph.add_node('process_input', process_input)
        self.graph.add_node('plan_smart_contract', plan_smart_contract)
        self.graph.add_node('code_node', code_node)
        self.graph.add_node('deploy_smart_contract', deploy_smart_contract)
        self.graph.add_node('get_feedback', get_feedback)
        self.graph.add_node('end', end_workflow)

        self.graph.add_edge('start', 'process_input')
        self.graph.add_edge('process_input', 'plan_smart_contract')
        
        self.graph.add_conditional_edges('plan_smart_contract', plan_approval_modifier)
        
        self.graph.add_conditional_edges('code_node', code_approval_modifier)

        self.graph.add_edge('deploy_smart_contract', 'get_feedback')
        self.graph.add_edge('get_feedback', 'end')

        self.graph.set_entry_point('start')

    def start(self, message: dict = {}):
        thread_id = stripped_uuid4()
        config = {"configurable": {"thread_id": thread_id}}
        if message:
            json_message = json.loads(message)
            initial_message = BaseMessage(content=json_message.get("content", {}), type=json_message.get(
            "type", ""), role=json_message.get("role", ""), file=json_message.get("file", ""))
            initial_state = WorkflowState(
                wallet_id=self.wallet_id,
                messages=[initial_message],
                elementDOM=None,
                intent=[],
                improved_prompt="",
                updated_style={},
                updated_content=""
            )
            latest_event = None
            for event in self.workflow_instance.stream(initial_state, config, stream_mode="values"):
                latest_event = event
            return thread_id, latest_event
        else:
            initial_state = WorkflowState(
                wallet_id=self.wallet_id,
                messages=[],
                elementDOM=None,
                intent=[],
                improved_prompt="",
                updated_style={},
                updated_content=""
            )
            latest_event = None
            for event in self.workflow_instance.stream(initial_state, config, stream_mode="values"):
                latest_event = event
            return thread_id, latest_event

    def chat(self, thread_id: str, message: dict, file: Optional[str] = None):
        config = {"configurable": {"thread_id": thread_id}}
        curr_state = self.workflow_instance.get_state(config)
        values = curr_state.values
        json_message = json.loads(message)
        if values.get("finished"):
            if values["finished"] is True:
                return "Chat has ended"
        messages = values.get("messages", [])
        if message:
            user_message = BaseMessage(content=json_message.get(
                "content", ""), type=json_message.get("type", ""), role=json_message.get("role", ""), file=json_message.get("file", ""))
            messages.append(user_message)
            self.workflow_instance.update_state(
                config=config, values={**values, "messages": messages})
        if file:
            self.workflow_instance.update_state(
                config=config, values={**values, "file": file})
        latest_event = None
        for event in self.workflow_instance.stream(None, config, stream_mode="values"):
            latest_event = event
        return latest_event