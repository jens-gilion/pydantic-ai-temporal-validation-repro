# pydantic_ai + Temporal: Structured Output Validation Runs in Workflow

Minimal reproduction showing that structured output validation runs inside the workflow rather than as an activity.

## Issue

When using `TemporalAgent` from pydantic_ai, output validation (pydantic model parsing) executes in the workflow context instead of being wrapped as an activity.

**Current behavior**:
1. Model call runs as an activity → succeeds
2. Validation runs in workflow → fails
3. pydantic_ai retries internally (model call activity runs again → succeeds)
4. Validation in workflow → fails again
5. After max retries exhausted, **workflow fails** with `UnexpectedModelBehavior`

**Consequence**: When validation ultimately fails, it's a workflow-level failure, not an activity failure. This means Temporal's activity retry policies, timeouts, and error handling don't apply to validation failures.

## Why This Matters

In Temporal, the typical pattern for "retry A if B fails" requires both to be activities:

```python
for attempt in range(max_retries):
    model_output = await workflow.execute_activity(call_model, ...)
    try:
        return await workflow.execute_activity(validate, model_output, ...)
    except ActivityError:
        continue  # Retry model call
```

With validation running in the workflow itself, this pattern isn't possible. A validation failure crashes the workflow rather than failing an activity that could trigger retry logic.

This may be intentional design - if so, consider this a feature request to move validation into an activity boundary.

## Reproduction Steps

### 1. Start Temporal

```bash
docker compose up -d
```

UI available at http://localhost:8299

### 2. Run the worker

```bash
uv run python worker.py
```

### 3. Trigger the workflow

```bash
uv run python trigger.py
```

### 4. Observe the failure

Check the Temporal UI - the workflow fails with:

```
UnexpectedModelBehavior: Exceeded maximum retries (1) for output validation
```

Caused by:
```
ValidationError: 1 validation error for ImpossibleOutput
  Value error, Intentional validation failure to reproduce bug
```

## Files

- `agent.py` - Agent with output schema that always fails validation (via `@model_validator`)
- `workflow.py` - Simple workflow that calls the agent
- `worker.py` - Temporal worker setup

## Environment

- Python 3.12
- pydantic-ai 1.23.0
- temporalio >= 1.11.0
- Vertex AI (gemini-2.0-flash)
