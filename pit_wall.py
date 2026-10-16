from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool

# Local Llama 3.1 via Ollama.
# CrewAI Agents reject langchain_community.llms.Ollama (ValidationError);
# use crewai.LLM with the same local model endpoint instead.
llm_local = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434",
)


@tool("Read Telemetry")
def read_telemetry() -> str:
    """Read the most recent F1 2018 telemetry frame from the shared buffer."""
    from telemetry_starter import telemetry_buffer

    if not telemetry_buffer:
        return "No telemetry data available in the buffer."
    return str(telemetry_buffer[-1])


telemetry_data_engineer = Agent(
    role="Telemetry Data Engineer",
    goal=(
        "Read the current telemetry using the available tool and summarize "
        "the car's state clearly for race strategy."
    ),
    backstory=(
        "You are a specialist in F1 2018 telemetry. You extract vital signals "
        "from live packets and turn them into concise, accurate summaries."
    ),
    tools=[read_telemetry],
    llm=llm_local,
    allow_delegation=False,
    verbose=True,
)

chief_race_strategist = Agent(
    role="Chief Race Strategist",
    goal=(
        "Make tactical decisions such as pushing or pitting based strictly "
        "on the Data Engineer's telemetry summary."
    ),
    backstory=(
        "You are a calm pit-wall strategist. You never invent telemetry; "
        "you only decide from the summary you are given."
    ),
    llm=llm_local,
    allow_delegation=False,
    verbose=True,
)

task_extract_telemetry = Task(
    description=(
        "Use the Leer Telemetria tool to extract vital parameters from the "
        "latest F1 2018 telemetry frame and write a concise summary of the "
        "car's current state."
    ),
    expected_output=(
        "A short summary of key telemetry parameters (speed, tires, fuel, "
        "temperatures, and any alerts if present)."
    ),
    agent=telemetry_data_engineer,
)

task_strategy_directive = Task(
    description=(
        "Analyze the Data Engineer's telemetry summary and output a clear "
        "directive for the driver (for example: push, hold pace, or pit)."
    ),
    expected_output=(
        "A single clear strategic directive for the driver, with a brief "
        "justification grounded in the telemetry summary."
    ),
    agent=chief_race_strategist,
    context=[task_extract_telemetry],
)

crew = Crew(
    agents=[telemetry_data_engineer, chief_race_strategist],
    tasks=[task_extract_telemetry, task_strategy_directive],
    process=Process.sequential,
    verbose=True,
)


if __name__ == "__main__":
    result = crew.kickoff()
    print("\n=== Final strategic decision ===")
    print(result)
