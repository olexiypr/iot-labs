from pydantic import BaseModel

from ..entities.agent_data import AgentData


class ProcessedAgentData(BaseModel):
    road_state: str
    air_quality: str
    agent_data: AgentData
