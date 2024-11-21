import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define DamagedNode class with population attribute
class DamagedNode:
    def __init__(self, name, damage_state, repair_time, importance, population_served):
        self.name = name
        self.damage_state = damage_state
        self.base_repair_time = repair_time
        self.repair_time = repair_time  # Set initial repair time to base repair time
        self.importance = importance
        self.population_served = population_served

# Define EPNNetwork class with stochastic elements
class EPNNetwork:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node):
        # Ensure every node has a 'repair_time' attribute set to its base value
        self.graph.add_node(node.name, 
                            damage_state=node.damage_state, 
                            base_repair_time=node.repair_time, 
                            repair_time=node.repair_time, 
                            importance=node.importance, 
                            population_served=node.population_served,
                            repaired=False)

    def add_edge(self, node1_name, node2_name):
        self.graph.add_edge(node1_name, node2_name)

    def apply_random_failure_delay(self, node_name):
        # Apply a random delay to the repair time of a node
        delay_factor = random.uniform(0.8, 1.5)  # Delay factor between 80% and 150% of base time
        self.graph.nodes[node_name]['repair_time'] = self.graph.nodes[node_name]['base_repair_time'] * delay_factor

    def propagate_damage(self, node_name, damage_probability=0.2):
        # Propagate damage to neighboring nodes with a certain probability
        for neighbor in self.graph.neighbors(node_name):
            # Skip if neighbor is already permanently repaired
            if self.graph.nodes[neighbor]['damage_state'] == "damaged" or self.graph.nodes[neighbor].get('repaired', False):
                continue
            if random.random() < damage_probability:
                self.graph.nodes[neighbor]['damage_state'] = "damaged"
                logging.info(f"Damage propagated to {neighbor} due to failure at {node_name}")

# Base heuristic prioritizing important nodes
def base_heuristic(network, available_resources):
    damaged_nodes = [node for node, data in network.graph.nodes(data=True) if data['damage_state'] == "damaged"]
    damaged_nodes.sort(key=lambda x: network.graph.nodes[x]['importance'], reverse=True)
    return damaged_nodes[:available_resources]

# Rollout algorithm with probabilistic repair and cascading failure
def rollout_algorithm(network, available_resources, steps=5):
    actions = []
    total_restoration_time = 0
    total_population_restored = 0

    for t in range(steps):
        action = base_heuristic(network, available_resources)
        if not action:
            break
        
        logging.info(f"Attempting to repair nodes: {action}")

        min_cost = float('inf')
        best_action = []
        for node in action:
            # Check if node has already been permanently repaired to avoid repeat repairs
            if network.graph.nodes[node].get('repaired', False):
                continue

            # Apply random repair delay and attempt probabilistic repair
            network.apply_random_failure_delay(node)
            repair_time = network.graph.nodes[node]['repair_time']
            
            # Simulate probabilistic repair outcome (80% chance of success)
            success_probability = 0.8
            if random.random() < success_probability:
                network.graph.nodes[node]['damage_state'] = "repaired"  # Simulate repair
                cost = calculate_cost_to_go(network)
                network.graph.nodes[node]['damage_state'] = "damaged"  # Revert state after simulation

                if cost < min_cost:
                    min_cost = cost
                    best_action = [node]
            else:
                logging.info(f"Repair on {node} failed due to probabilistic outcome.")

        # Apply best action and update states
        for node in best_action:
            network.graph.nodes[node]['damage_state'] = "repaired"
            network.graph.nodes[node]['repaired'] = True  # Mark node as permanently repaired
            actions.append(node)
            total_restoration_time += network.graph.nodes[node]['repair_time']
            total_population_restored += network.graph.nodes[node]['population_served']

            # Propagate damage to neighbors
            network.propagate_damage(node)

        logging.info(f"Repaired Nodes: {best_action}")
        logging.info(f"Total Restoration Time after this step: {total_restoration_time:.2f} days")
        logging.info(f"Total Population Restored after this step: {total_population_restored}")

    return actions, total_restoration_time, total_population_restored

# Approximate cost-to-go function based on repair time and importance
def calculate_cost_to_go(network):
    total_cost = 0
    for node, data in network.graph.nodes(data=True):
        if data['damage_state'] == "damaged":
            total_cost += data['repair_time'] * (10 - data['importance'])
            # Add penalty for each damaged neighbor
            neighbors = list(network.graph.neighbors(node))
            for neighbor in neighbors:
                if network.graph.nodes[neighbor]['damage_state'] == "damaged":
                    total_cost += 5  # Penalty for adjacent damaged nodes
    return total_cost

# Visualize the network with color intensity based on repair order
def visualize_network(network, title="Network State", repair_order=None):
    color_map = []
    if repair_order:
        for node in network.graph.nodes():
            if node in repair_order:
                # Color intensity based on repair order (earlier repairs are darker green)
                index = repair_order.index(node)
                intensity = 1 - (index / len(repair_order)) * 0.5  # Lighter green for later repairs
                color_map.append((0, intensity, 0))  # RGB for varying green intensity
            else:
                # Damaged nodes are red
                color_map.append('red')
    else:
        # Default coloring if no repair order is provided
        color_map = ['green' if data['damage_state'] == "repaired" else 'red'
                     for _, data in network.graph.nodes(data=True)]
    
    pos = nx.spring_layout(network.graph)  # Layout for visual clarity
    plt.figure(figsize=(10, 8))
    nx.draw(network.graph, pos, node_color=color_map, node_size=1400, font_size=10, font_color='white')
    
    labels = {node: f"{node}\nPopulation: {data['population_served']}" for node, data in network.graph.nodes(data=True)}
    nx.draw_networkx_labels(network.graph, pos, labels=labels, font_size=10)
    
    plt.title(title)
    plt.show()

# Main function to run ADP and rollout simulation with outputs for restoration time and population restored
def simulate_recovery_with_adp():
    # Initialize network and nodes
    network = EPNNetwork()
    nodes = [
        DamagedNode("EPN-1", "damaged", 30, 5, 300),
        DamagedNode("EPN-2", "damaged", 1, 3, 100),
        DamagedNode("EPN-3", "damaged", 1, 2, 50),
        DamagedNode("EPN-4", "damaged", 0.5, 1, 50),
        DamagedNode("EPN-5", "damaged", 1, 4, 100),
        DamagedNode("EPN-6", "damaged", 0.5, 1, 50),
        DamagedNode("EPN-7", "damaged", 1, 4, 100),
        DamagedNode("EPN-8", "damaged", 7, 5, 200),
        DamagedNode("EPN-9", "damaged", 0.5, 2, 30),
        DamagedNode("EPN-10", "damaged", 0.5, 2, 30),
        DamagedNode("EPN-11", "damaged", 3, 3, 80),
        DamagedNode("EPN-12", "damaged", 30, 5, 300),
    ]

    # Add nodes and edges to the network
    for node in nodes:
        network.add_node(node)

    network.add_edge("EPN-1", "EPN-2")
    network.add_edge("EPN-1", "EPN-3")
    network.add_edge("EPN-2", "EPN-4")
    network.add_edge("EPN-2", "EPN-5")
    network.add_edge("EPN-3", "EPN-6")
    network.add_edge("EPN-5", "EPN-11")
    network.add_edge("EPN-6", "EPN-12")
    network.add_edge("EPN-8", "EPN-1")
    network.add_edge("EPN-9", "EPN-2")
    network.add_edge("EPN-10", "EPN-3")
    network.add_edge("EPN-10", "EPN-7")

    # Display initial damaged network
    visualize_network(network, "Initial Network State (Damaged Nodes)")
    available_resources = 5
    steps = 5
    optimal_actions, final_restoration_time, total_population_restored = rollout_algorithm(network, available_resources, steps)

    # Display final repaired network with repair order
    visualize_network(network, "Final Network State (Repaired Nodes with Repair Order)", repair_order=optimal_actions)

    # Run the rollout algorithm with ADP
# Display order of repaired nodes and summary statistics
    print("Order of Repaired Nodes:", optimal_actions)
    print(f"Total Restoration Time: {final_restoration_time:.2f} days")
    print(f"Total Population Restored: {total_population_restored}")

# Run the simulation
simulate_recovery_with_adp()