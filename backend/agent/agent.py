from google.adk.agents import LlmAgent
from agent.prompt import ROOT_AGENT_PROMPT
from agent.tools import (
    get_all_events,
    create_event_tool,
    events_by_location,
    events_by_month,
    check_event_exists,
    update_event_location,
    delete_event_by_title
)
from constants import AGENT_NAME, AGENT_DESCRIPTION, AGENT_MODEL

# Register tools in a list the agent can call
root_agent = LlmAgent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    description=AGENT_DESCRIPTION,
    instruction=ROOT_AGENT_PROMPT,
    tools=[
        get_all_events,
        create_event_tool,
        events_by_location,
        events_by_month,
        check_event_exists,
        update_event_location,
        delete_event_by_title
    ]
)
