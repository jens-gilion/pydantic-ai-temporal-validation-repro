"""Workflow definition with sandbox-safe imports."""

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from agent import temporal_agent


@workflow.defn
class BugReproWorkflow:
    """Workflow that runs the agent - will crash entirely on validation failure."""

    @workflow.run
    async def run(self) -> str:
        # This should fail the activity, not crash the workflow
        result = await temporal_agent.run(
            user_prompt="Generate the output.",
        )
        return str(result.output)

