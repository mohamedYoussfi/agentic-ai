import asyncio
import streamlit as st
from openai.types.responses import ResponseTextDeltaEvent
from agents.mcp import MCPServer, MCPServerStdio, MCPServerSse
import sys
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ("API KEY not available")
# Add the parent directory to the path so we can import the agents module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent, Runner

st.set_page_config(
    page_title="Agent Demo",
    page_icon=".",
    layout="wide",
)

st.title("Agent Demo")
st.write("See the streaming capabilities of OpenAI Agents with visual effects.")


with st.sidebar:
    demo_options = [
        "List of files",
        "if not created, create new file data.txt",
        "content of data.txt file",
        "Look at my favorite songs. Suggest one new song that I might like.",
    ]
    demo_prompt = st.selectbox("Quick Prompts", demo_options)

    st.markdown("---")
    st.markdown("Made with  using OpenAI Agents")

# User input area
user_input = st.text_area("Your message:", value=demo_prompt, height=100)
send_button = st.button("Send", type="primary")

# Response area with custom styling
response_container = st.container()
message_placeholder = st.empty()

import asyncio
import os
import shutil

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio
from dotenv import load_dotenv

load_dotenv()


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="answer the user question using provided tools",
        mcp_servers=[mcp_server],
    )

    if send_button and user_input:

        with response_container:

            with st.spinner("Thinking..."):
                result = await Runner.run(starting_agent=agent, input=user_input)
                print(result.final_output)
                message_placeholder.markdown(result.final_output)

            # Add clear button
            if st.button("Clear"):
                st.experimental_rerun()

    # Instructions
    if not send_button:
        with response_container:
            st.info(
                "👆 Enter your message above and click 'Send' to see the streaming response."
            )
            st.markdown(
                """
            ### Tips:
            - Choose from the quick prompts or enter your own
            - Try complex prompts to see how the agent responds in real-time
            """
            )


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_files")
    os.makedirs(samples_dir, exist_ok=True)
    async with MCPServerStdio(
        name="Filesystem Server, via npx",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP Filesystem Example", trace_id=trace_id):
            print(
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n"
            )
            await run(server)


if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError(
            "npx is not installed. Please install it with `npm install -g npx`."
        )

    asyncio.run(main())
