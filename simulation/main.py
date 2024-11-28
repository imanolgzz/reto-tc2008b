from warehouse.model import Maze

# Set the parameters for the simulation
model_params = {
    "lgvs": 3,     # Number of bots
    "time": 12,    # Simulation time in minutes
}

# Initialize the model
maze_model = Maze(**model_params)

# Run the simulation for a given number of steps
for step in range(8000):  # Adjust the number of steps as needed
    print(f"Step {step + 1}")
    maze_model.step()
    
    # Stop if all agents are done
    if not maze_model.running:
        print("Simulation finished.")
        break
