from google.adk.agents import LlmAgent
from agent.prompt import ROOT_AGENT_PROMPT
from agent.tools import (
    get_all_events,
    create_event_tool,
    events_by_location,
    events_by_month,
    check_event_exists,
    update_event_location,
    delete_event_by_title,
    total_events_count,
    events_this_month,
    city_with_most_events,
    top_performer,
    most_recently_added_event,
    events_created_last_n_days,
    location_with_most_past_events,
    create_organizer_tool,
    list_organizers_tool,
    events_managed_by_company_tool,
    region_with_max_cultural_events_tool,
    top_organizer_2025_tool,
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
        delete_event_by_title,
        total_events_count,
        events_this_month,
        city_with_most_events,
        top_performer,
        most_recently_added_event,
        events_created_last_n_days,
        location_with_most_past_events,
        create_organizer_tool,
        list_organizers_tool,
        events_managed_by_company_tool,
        region_with_max_cultural_events_tool,
        top_organizer_2025_tool,
    ]
)
