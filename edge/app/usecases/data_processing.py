from ..entities.agent_data import AgentData
from ..entities.processed_agent_data import ProcessedAgentData


def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    air_quality = 'GOOD AIR'
    if agent_data.aq.co2_level > 1500:
        air_quality = 'BAD AIR'

    if 10000 < agent_data.accelerometer.z < 15000:
        road_state = 'OK'
    elif agent_data.accelerometer.z > 15000:
        road_state = 'BUMP'
    else:
        road_state = 'POTHOLE'

    return ProcessedAgentData(
        road_state=road_state,
        air_quality=air_quality,
        agent_data=agent_data,
    )
