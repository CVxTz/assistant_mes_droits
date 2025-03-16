from langchain_core.messages import HumanMessage

from assistant_mes_droits.agent.mes_droits_agent import (
    AgentState,
    MesDroitsAgent,
    search,
)


def build_agent():
    agent = MesDroitsAgent(search_tools=[search])

    return agent.graph


if __name__ == "__main__":
    _agent = build_agent()

    initial_state = AgentState(
        messages=[HumanMessage(content="J'ai du mal a payer mes factures, que faire ?")]
    )

    config = {"configurable": {"thread_id": "1"}}

    state_dict = _agent.invoke(initial_state, config=config)

    state = AgentState(**state_dict)

    for message in state.messages:
        print(message)
