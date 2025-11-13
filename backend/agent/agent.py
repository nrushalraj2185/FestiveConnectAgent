from google.adk.agents import LlmAgent
from agent.prompt import *
from agent.tools import *
from constants import AGENT_NAME, AGENT_DESCRIPTION, AGENT_MODEL

root_agent = LlmAgent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    description=AGENT_DESCRIPTION,
    instruction=ROOT_AGENT_PROMPT,
    tools=[
        get_all_events,create_event,get_event,update_event,
        delete_event,get_total_events,get_events_this_month,get_city_with_most_events,
        get_top_performer,get_most_recent_event,get_recent_events_15_days,
        get_location_with_most_past_events
    ]
)
