from google.adk.agents import ParallelAgent, SequentialAgent

from delve.agents.deployment_agent import deployment_agent
from delve.agents.log_agent import log_agent
from delve.agents.metrics_agent import metrics_agent
from delve.agents.root_cause_agent import root_cause_agent

parallel_investigation = ParallelAgent(
    name="parallel_investigation",
    sub_agents=[log_agent, metrics_agent, deployment_agent],
)

investigation_team = SequentialAgent(
    name="investigation_team",
    sub_agents=[parallel_investigation, root_cause_agent],
)