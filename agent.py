"""Agent definition - separated to avoid sandbox issues."""

from pydantic import BaseModel, model_validator
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import AgentPlugin, TemporalAgent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


# Output schema that always fails validation
class ImpossibleOutput(BaseModel):
    """Schema with a validator that always fails."""

    value: str

    @model_validator(mode="after")
    def always_fail(self) -> "ImpossibleOutput":
        raise ValueError("Intentional validation failure to reproduce bug")


# Create agent with impossible output schema using Vertex AI
provider = GoogleProvider(vertexai=True)
model = GoogleModel("gemini-2.0-flash", provider=provider)

agent = Agent(
    model,
    name="bug-repro-agent",
    output_type=ImpossibleOutput,
    instructions="Return any value string.",
    retries=1,
)
temporal_agent = TemporalAgent(agent)


def get_plugin() -> AgentPlugin:
    return AgentPlugin(agent=temporal_agent)

