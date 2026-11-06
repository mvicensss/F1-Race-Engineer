from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool

# Local Llama 3.1 via Ollama.
# CrewAI Agents reject langchain_community.llms.Ollama (ValidationError);
# use crewai.LLM with the same local model endpoint instead.
llm_local = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434",
)

# fetch the lastest telemetry packet + one script for the entry block
@tool("Read Telemetry") #TOOL THAT CAN BE CALLED BY THE AGENT
# fetch last packet
def read_telemetry() -> str:
    """Read the most recent F1 2018 telemetry frame from the shared buffer."""
    from telemetry_starter import telemetry_buffer

    if not telemetry_buffer:
        return "No telemetry data available in the buffer."
    return str(telemetry_buffer[-1]) #return the last packet in the buffer as a string (-1 means the last one)

#CrewAI agent -- Telemetry Data Engineer == Summarizes current telemetry
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
    allow_delegation=False, #won't delegate task on another agent, will do it itself
    verbose=True, #will print reasoning and output to console for debugging
)

#CrewAI agent -- Chief Race Strategist == Makes decisions based on telemetry summary (push, hold or pit?)
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
    #no direct tool usage, because it relies on the summary from the previous agent
    llm=llm_local,
    allow_delegation=False,
    verbose=True,
)

#CrewAI task -- Extract telemetry and summarize. Assigned to the Telemetry Data Engineer (agent 1)
task_extract_telemetry = Task(
    description=(
        "Use the Read Telemetry tool to extract vital parameters from the "
        "latest F1 2018 telemetry frame and write a concise summary of the "
        "car's current state."
    ),
    expected_output=(
        "A short summary of key telemetry parameters (speed, tires, fuel, "
        "temperatures, and any alerts if present)."
    ),
    agent=telemetry_data_engineer, #assigned to the telemetry data engineer agent
)

#CrewAI task -- Analyze telemetry summary and output directive. Assigned to the Chief Race Strategist (agent 2)
task_strategy_directive = Task(
    description=(
        "Analyze the Data Engineer's telemetry summary and output a clear "
        "directive for the driver (for example: push, hold pace, or pit)."
    ),
    expected_output=(
        "A single clear strategic directive for the driver, with a brief "
        "justification grounded in the telemetry summary."
    ),
    agent=chief_race_strategist, #assigned to the chief race strategist agent
    context=[task_extract_telemetry], #the context is the output of the previous task, which is the telemetry summary from the telemetry data engineer
)

#CrewAI Crew -- Combines the two agents and their tasks into a sequential process
crew = Crew(
    agents=[telemetry_data_engineer, chief_race_strategist],
    tasks=[task_extract_telemetry, task_strategy_directive],
    process=Process.sequential,
    verbose=True, #print reasoning and output to console for debugging
)

# Run the Crew to get the final strategic decision // execution trigger
if __name__ == "__main__":
    result = crew.kickoff()
    print("\n=== Final strategic decision ===")
    print(result)
