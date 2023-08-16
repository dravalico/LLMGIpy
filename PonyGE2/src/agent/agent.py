from fitness.evaluation import evaluate_fitness
from operators.crossover import crossover
from operators.initialisation import initialisation
from operators.mutation import mutation
from operators.replacement import replacement
from operators.selection import selection
from stats.stats import get_stats


class Agent:
    """
    Class representing individual robots/agents. The agents has three main
    methods.

    Sense   - method responsible for getting information from the environment
              from different sensors
    Act     - method responsible to process the information given by Sense
              method
    Update  - method responsible to update the state of the agent
    """

    def __init__(self, ip):
        # Interaction probability received in constructor
        self.interaction_probability = ip

        # Only initialize single individual. Single agent can only have single
        # genetic information
        self.individual = initialisation(1)

        # Evaluate the fitness for the the individual    
        self.individual = evaluate_fitness(self.individual)

        # Flag which store the boolean value for other neighbouring agents
        # found or not
        self.agents_found = False

    def sense(self, agents):
        # This part makes this GE algorithm useful for multi-agent systems.
        # This method is responsible to sense information from the environment
        # This method would be overridden by actual robots following the
        # different logic for near by agents discovery

        import random

        # Logic that defines how a agent discovers nearby agents
        # If the random value is greater than the interaction probability
        # parameter that denotes the agent has found some nearby agents.
        # Higher the probability, better the chance of agent to share its
        # genome with other agents
        if random.random() > self.interaction_probability:
            # Turn the flag to True
            self.agents_found = True

            # Getting values to sample agents for interaction
            range_min = int((self.interaction_probability * len(agents)) / 3)
            range_max = int((self.interaction_probability * len(agents)) / 2)
            range_avg = int((range_min + range_max) / 2)

            # Sample the agents from the list of agents. The number of samples
            # depend on above values
            no_agents_found = random.sample(range(len(agents)), random.choice(
                [range_min, range_max, range_avg]))

            # Extract the individuals from the nearby agents and store the
            # individuals in the class variable
            self.nearby_agents = [agents[id].individual[0] for id in
                                  no_agents_found]

    def act(self):
        # Process the information if the agent has sense nearby agents
        if self.agents_found:
            # Combine the original individual and individuals found by
            # interacting with nearby agents to form a population
            individuals = self.individual + self.nearby_agents

            # Find out parents from the population
            parents = selection(individuals)

            # Crossover parents and add to the new population.
            cross_pop = crossover(parents)

            # Mutate the new population.
            new_pop = mutation(cross_pop)

            # Evaluate the fitness of the new population.
            new_pop = evaluate_fitness(new_pop)

            # Replace the old population with the new population.
            individuals = replacement(new_pop, individuals)

            # Generate statistics for run so far
            get_stats(individuals)

            # Sort the individuals list 
            individuals.sort(reverse=True)

            # Get the highest performing individual from the sorted population
            self.new_individual = individuals[0]

    def update(self):
        # Update the information if the agent has sense nearby agents
        if self.agents_found:
            # Replace the individual with the highest performing individual
            # obtained from act method
            self.individual = [self.new_individual]
