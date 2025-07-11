# chat_agent.py
# This file creates an LLM-powered agent that can interact with SharePoint through custom tools

from langchain.llms import Ollama
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import SystemMessagePromptTemplate, MessagesPlaceholder, ChatPromptTemplate
from app.sharepoint_client import SharePointClient

def create_llm_agent():
    # Initialize the Ollama LLM with the gemma3 model
    # The base_url points to the Ollama service defined in Docker Compose
    llm = Ollama(model="gemma3", base_url="http://ollama:11434")
    
    # Create a SharePoint client to interact with SharePoint services
    sp_client = SharePointClient()

    # Define a tool function that searches SharePoint document libraries
    # This will be exposed to the LLM agent for document searches
    def search_documents_tool(query: str):
        # Search the "Documents" library and convert results to markdown for display
        return sp_client.search_documents("Documents", query).to_markdown(index=False)

    # Define a tool function that lists items from a SharePoint list
    # This will be exposed to the LLM agent for retrieving list items
    def list_items_tool(query: str):
        # Get items from the "Onboarding Checklist" list and convert to markdown
        return sp_client.list_items("Onboarding Checklist").to_markdown(index=False)

    # Create a list of tools that the agent can use
    tools = [
        Tool(
            name="SearchDocuments",
            func=search_documents_tool,
            description="Search SharePoint document libraries for files by name."
        ),
        Tool(
            name="ListSharePointItems",
            func=list_items_tool,
            description="List SharePoint custom list items."
        )
    ]
    
    # Create a memory buffer to store conversation history
    # This allows the agent to reference previous messages
    memory = ConversationBufferMemory(memory_key="chat_history")

    # --- Custom prompt ---
    # Define the system prompt that sets the behavior and capabilities of the agent
    system_prompt = """
    You are an expert SharePoint assistant. 
    Always answer user questions about documents or lists in a helpful, concise, and professional manner.
    If you use a tool, clearly reference the results.
    """

    # Create a custom chat prompt template that includes the system prompt and chat history
    # This template structures how the agent receives and processes messages
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
    ])

    # Initialize the LangChain agent with the tools, LLM, and prompt
    # The "zero-shot-react-description" agent type can use tools based on their descriptions
    agent = initialize_agent(
        tools,
        llm,
        agent="zero-shot-react-description",
        memory=memory,
        prompt=chat_prompt,
        verbose=True  # Enable verbose mode to see the agent's thought process
    )
    return agent
