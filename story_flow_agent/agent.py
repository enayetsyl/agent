import os
import logging
from typing import AsyncGenerator
from google.adk.agents import LlmAgent, BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model to use (can be overridden via environment variable)
MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-2.0-flash-001")


class StoryFlowAgent(BaseAgent):
    """
    A custom agent that orchestrates a multi-stage story generation workflow
    with conditional logic for regeneration based on tone checks.

    This agent demonstrates:
    - Custom orchestration logic beyond standard workflow agents
    - Conditional branching based on state
    - Using LoopAgent and SequentialAgent as sub-agents
    - State management across multiple sub-agents
    """

    # Field declarations for Pydantic
    story_generator: LlmAgent
    critic: LlmAgent
    reviser: LlmAgent
    grammar_check: LlmAgent
    tone_check: LlmAgent
    loop_agent: LoopAgent
    sequential_agent: SequentialAgent

    # Allow arbitrary types for agent instances
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        story_generator: LlmAgent,
        critic: LlmAgent,
        reviser: LlmAgent,
        grammar_check: LlmAgent,
        tone_check: LlmAgent,
    ):
        """
        Initialize the StoryFlowAgent with its sub-agents.

        Args:
            name: The name of the agent
            story_generator: LlmAgent that generates the initial story
            critic: LlmAgent that critiques the story
            reviser: LlmAgent that revises the story based on criticism
            grammar_check: LlmAgent that checks grammar
            tone_check: LlmAgent that analyzes the tone
        """
        # Create internal workflow agents before calling super().__init__
        loop_agent = LoopAgent(
            name="CriticReviserLoop",
            sub_agents=[critic, reviser],
            max_iterations=2
        )
        sequential_agent = SequentialAgent(
            name="PostProcessing",
            sub_agents=[grammar_check, tone_check]
        )

        # Define the top-level sub-agents list
        sub_agents_list = [
            story_generator,
            loop_agent,
            sequential_agent,
        ]

        # Initialize BaseAgent with sub-agents
        super().__init__(
            name=name,
            story_generator=story_generator,
            critic=critic,
            reviser=reviser,
            grammar_check=grammar_check,
            tone_check=tone_check,
            loop_agent=loop_agent,
            sequential_agent=sequential_agent,
            sub_agents=sub_agents_list,
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Implements the custom orchestration logic for the story workflow.
        This is where the conditional logic happens!
        """
        logger.info(f"[{self.name}] Starting story generation workflow.")

        # Step 1: Generate the initial story
        logger.info(f"[{self.name}] Running StoryGenerator...")
        async for event in self.story_generator.run_async(ctx):
            yield event

        # Check if story was generated before proceeding
        if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
            logger.error(f"[{self.name}] Failed to generate initial story. Aborting workflow.")
            return

        logger.info(f"[{self.name}] Story state after generator: {ctx.session.state.get('current_story')}")

        # Step 2: Critic-Reviser Loop (runs critic and reviser up to 2 times)
        logger.info(f"[{self.name}] Running CriticReviserLoop...")
        async for event in self.loop_agent.run_async(ctx):
            yield event

        logger.info(f"[{self.name}] Story state after loop: {ctx.session.state.get('current_story')}")

        # Step 3: Sequential Post-Processing (Grammar and Tone Check)
        logger.info(f"[{self.name}] Running PostProcessing...")
        async for event in self.sequential_agent.run_async(ctx):
            yield event

        # Step 4: Conditional Logic - Regenerate if tone is negative
        tone_check_result = ctx.session.state.get("tone_check_result", "").strip().lower()
        logger.info(f"[{self.name}] Tone check result: {tone_check_result}")

        if tone_check_result == "negative":
            logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
            # Regenerate the story by running the generator again
            async for event in self.story_generator.run_async(ctx):
                yield event
        else:
            logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")

        logger.info(f"[{self.name}] Workflow finished.")


# Define the individual LLM sub-agents
story_generator = LlmAgent(
    name="StoryGenerator",
    model=MODEL,
    instruction=(
        "You are a creative story writer. Write a short story (around 100-150 words) "
        "based on the topic provided by the user in their message or in session state with key 'topic'. "
        "Extract the topic from the user's message if provided. Make it engaging and well-written."
    ),
    output_key="current_story"  # Stores output in session state
)

critic = LlmAgent(
    name="Critic",
    model=MODEL,
    instruction=(
        "You are a story critic. Review the story provided in session state with key 'current_story'. "
        "Provide 1-2 sentences of constructive criticism on how to improve it. "
        "Focus on plot, character development, or narrative flow."
    ),
    output_key="criticism"  # Stores criticism in session state
)

reviser = LlmAgent(
    name="Reviser",
    model=MODEL,
    instruction=(
        "You are a story reviser. Revise the story provided in session state with key 'current_story', "
        "based on the criticism in session state with key 'criticism'. "
        "Output only the revised story, making it better while keeping the core narrative."
    ),
    output_key="current_story"  # Overwrites the original story
)

grammar_check = LlmAgent(
    name="GrammarCheck",
    model=MODEL,
    instruction=(
        "You are a grammar checker. Check the grammar of the story provided in session state "
        "with key 'current_story'. Output only the suggested corrections as a list, "
        "or output 'Grammar is good!' if there are no errors."
    ),
    output_key="grammar_suggestions"
)

tone_check = LlmAgent(
    name="ToneCheck",
    model=MODEL,
    instruction=(
        "You are a tone analyzer. Analyze the tone of the story provided in session state "
        "with key 'current_story'. Output only one word: 'positive' if the tone is generally "
        "positive, 'negative' if the tone is generally negative, or 'neutral' otherwise."
    ),
    output_key="tone_check_result"  # This determines the conditional flow!
)

# Instantiate the custom agent with all sub-agents
root_agent = StoryFlowAgent(
    name="story_flow_agent",
    story_generator=story_generator,
    critic=critic,
    reviser=reviser,
    grammar_check=grammar_check,
    tone_check=tone_check,
)