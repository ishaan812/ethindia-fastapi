import json
import os
from typing import Annotated, List, Literal, Optional, TypedDict
from agents.workflows.researcher.nodes import usecase_buffer, usecase_generator, usecase_modifier, end_workflow,  start_workflow, process_input
from fastapi import HTTPException
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from agents.utils.helpers import is_json, stripped_uuid4
from agents.workflows.index import WorkflowInterface


class WorkflowState(TypedDict):
    messages: Annotated[list, add_messages]
    mermaid_input: str
    altered_mermaid: str
    options: list[dict]
    output: dict
    finished: bool
    


class ResearchWorkflow(WorkflowInterface):
    def __init__(self, Checkpointer):
        self.wallet_id = "facdbf29-1439-4a87-b2f6-f0360da57dc7"
        self.graph = StateGraph(WorkflowState)
        self._initialize_graph()
        self.workflow_instance = self.graph.compile(
            interrupt_before=["process_input", "usecase_buffer"],
            checkpointer=Checkpointer,
        )
        # self._save_workflow_diagram(os.path.dirname(__file__))


    def _initialize_graph(self):
        """Setup the state graph for the workflow process."""
        self.graph.add_node('start', start_workflow)
        self.graph.add_node('process_input', process_input)
        self.graph.add_node('usecases_generator', usecase_generator)
        self.graph.add_node("usecase_buffer", usecase_buffer)
        self.graph.add_node('end', end_workflow)

        self.graph.add_edge('start', 'process_input')
        self.graph.add_edge('process_input', 'usecases_generator')
        self.graph.add_edge("usecases_generator", "usecase_buffer")
        self.graph.add_conditional_edges('usecase_buffer', usecase_modifier)

        self.graph.set_entry_point('start')

    def start(self, message: dict = {}):
        thread_id = stripped_uuid4()
        config = {"configurable": {"thread_id": thread_id}}

        if message:
            json_message = json.loads(message)
            initial_message = BaseMessage(content=json_message.get("content", {}), type=json_message.get(
            "type", ""), role=json_message.get("role", ""), file=json_message.get("file", ""))
            initial_state = WorkflowState(
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