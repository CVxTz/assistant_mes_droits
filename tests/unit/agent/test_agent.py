from langchain_core.messages import AIMessage, HumanMessage

from assistant_mes_droits.agent.agent import build_agent
from assistant_mes_droits.agent.mes_droits_agent import AgentState


def test_build_agent_initializes_correctly():
    agent_graph = build_agent()

    assert agent_graph is not None
    assert hasattr(agent_graph, "invoke"), "Agent graph should have an invoke method"


def test_agent_processes_message_and_returns_response():
    agent_graph = build_agent()

    initial_state = AgentState(
        messages=[HumanMessage(content="J'ai du mal a payer mes factures, que faire ?")]
    )
    config = {"configurable": {"thread_id": "test_thread_1"}}

    # Invoke the agent and validate the response structure
    state_dict = agent_graph.invoke(initial_state, config=config)
    state = AgentState(**state_dict)

    # Basic response validation
    assert len(state.messages) > 1, "Should have more than initial message"
    assert any(
        isinstance(msg, AIMessage) for msg in state.messages
    ), "Should contain AI response"
    assert (
        "factures" in state.messages[-1].content.lower()
    ), "Response should be relevant to query"
