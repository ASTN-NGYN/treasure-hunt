from grid import Grid
from bayesian_agent import BayesianAgent
from experiment_runner import ExperimentRunner

print("Running quick test...")

grid = Grid(20)

agent = BayesianAgent(grid, 2, 0.1, 0.2)

for _ in range(10):
    agent.step()

print("Entropy history:", agent.entropy_history)

runner = ExperimentRunner(
    20,2,0.1,0.2,[1,2,3]
)

runner.run_experiments()

runner.print_results()

print("Test complete.")