def step(agents):
    """
    Runs a single generation of the evolutionary algorithm process
    """
    # Loop over all the agents and apply their generic methods in sequence
    for agent in agents:
        # Sense the environment
        agent.sense(agents)

        # Based on the values from the sensor perform action
        agent.act()

        # Update the state of the agent
        agent.update()

    return agents
