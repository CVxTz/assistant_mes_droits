import uuid
from operator import add
from typing import Annotated, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import BaseTool
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from assistant_mes_droits.agent.clients import client as global_client
from assistant_mes_droits.agent.clients import store
from assistant_mes_droits.logger import logger


@tool
def search(query: str) -> str:
    """
    Search in a vector store of French citizen rights. Use this tool to complement your answers.
    Generate your own queries to search the document database to better answer the user's questions.
    Always search first before answering.
    """
    logger.info(f"Executing search tool with query: '{query}'")  # Added log
    results = store.search(query, k=20)

    result = ""
    for doc in results:
        result += f"""{doc.metadata["title"]}\n{doc.page_content[:10_000]}"""

    return result


class AgentState(BaseModel):
    messages: Annotated[list, add] = Field(default_factory=list)


class Assertion(BaseModel):
    assertion: str
    source: Optional[str] = Field(
        description="URL source of the assertion, return None if no source is available."
    )


class Assertions(BaseModel):
    assertions: list[Assertion] = Field(default_factory=list)


class MesDroitsAgent:
    def __init__(self, search_tools: list[BaseTool], client=global_client):
        self.search_tools = search_tools
        self.tool_mapping = {_tool.name: _tool for _tool in self.search_tools}
        self.graph = None
        self.client = client
        self.build_agent()

    def generate_search_query(self, state: AgentState):
        local_client = self.client.bind_tools(self.search_tools, tool_choice="any")
        result = local_client.invoke(
            [
                SystemMessage(
                    content="""You are a helpful assistant. 
                        Use the search tool to find relevant context about the user's question. 
                        Answer in French. 
                        """
                )
            ]
            + state.messages
        )
        logger.info(
            f"Node 'generate_search_query': Generated message: {result}"
        )  # Added log
        return {"messages": [result]}

    def use_search_tool(self, state: AgentState):
        logger.info(
            f"Node 'use_search_tool': Starting. Last message: {state.messages[-1]}"
        )  # Added log
        tool_calls: AIMessage = state.messages[-1]
        results = []
        for tool_call in tool_calls.tool_calls:
            tool_name = tool_call["name"]
            _tool = self.tool_mapping[tool_name]
            logger.info(
                f"Node 'use_search_tool': Invoking tool '{tool_name}' with args: {tool_call}"
            )  # Added log (logs entire tool_call dict)
            tool_result = _tool.invoke(tool_call)
            logger.info(
                f"Node 'use_search_tool': Raw result from tool '{tool_name}': {tool_result}"
            )  # Added log
            results.append(tool_result)

        return {"messages": results}

    def generate_assertions(self, state: AgentState):
        local_client = self.client.with_structured_output(Assertions)
        result = local_client.invoke(
            [
                SystemMessage(
                    content=f"""You are a helpful assistant. 
                        Generate a list of assertions to answer the use's questions.
                        Cite the URL of the source for each of your assertions.
                        Never make an assertion that you can't cite from the search tool.
                        Answer in French.
                        Use this schema: {Assertions.model_json_schema()}
                        """
                )
            ]
            + state.messages
        )
        # Create the message first to log it before returning

        result.assertions = [x for x in result.assertions if x.source is not None]

        tool_message_content = (
            result.model_dump_json()
            if result.assertions
            else "No sourced assertions were found. Tell the the user that you cannot answer their questions."
        )
        _id = uuid.uuid4().hex
        ai_message = AIMessage(
            content="",
            tool_calls=[
                {"name": "summary", "args": {}, "id": _id, "type": "tool_call"}
            ],
        )
        tool_message = ToolMessage(content=tool_message_content, tool_call_id=_id)
        logger.info(
            f"Node 'generate_assertions': Generated message: {tool_message}"
        )  # Added log
        return {
            "messages": [ai_message, tool_message]
        }  # Return the already created message

    def generate_response(self, state: AgentState):
        local_client = self.client
        result = local_client.invoke(
            [
                SystemMessage(
                    content="""You are a helpful assistant. 
                        Generate a response to the user's question using the provided assertions.
                        Cite the URL of the source for each of your assertions in the form ( https://SOURCE_URL )
                        If you cannot find relevant information say to the user that you are unable to answer.
                        Write this as a single paragraph if possible.
                        Answer in French.
                        """
                )
            ]
            + state.messages
        )
        logger.info(
            f"Node 'generate_response': Generated message: {result}"
        )  # Added log
        return {"messages": [result]}

    def build_agent(self):
        logger.info("Building agent graph...")  # Added log
        builder = StateGraph(AgentState)
        builder.add_node("generate_search_query", self.generate_search_query)
        builder.add_node("use_search_tool", self.use_search_tool)
        builder.add_node("generate_assertions", self.generate_assertions)
        builder.add_node("generate_response", self.generate_response)

        builder.add_edge(START, "generate_search_query")
        builder.add_edge("generate_search_query", "use_search_tool")
        builder.add_edge("use_search_tool", "generate_assertions")
        builder.add_edge("generate_assertions", "generate_response")
        builder.add_edge("generate_response", END)

        self.graph = builder.compile()


if __name__ == "__main__":
    agent = MesDroitsAgent(search_tools=[search])

    initial_state = AgentState(
        messages=[HumanMessage(content="est ce qu'il y'a une periode d'essaie?")],
    )

    output_state = agent.graph.invoke(initial_state)

    for message in output_state["messages"]:
        print(message.type)
        print(message.content)
        if isinstance(message, AIMessage):
            print(message.tool_calls)
