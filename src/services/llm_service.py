"""
Enhanced LLM service with error handling, validation, and retry logic.
Provides robust LLM interactions with fallback mechanisms.
"""

import time
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

from langchain.llms import Ollama
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    ChatPromptTemplate,
)
from langchain.schema import AgentAction, AgentFinish

from ..core import (
    config_manager,
    LLMConstants,
    LLMConnectionError,
    LLMTimeoutError,
    LLMResponseError,
    get_logger,
    log_performance,
    log_function_call,
)
from ..utils import validate_user_input
from ..clients import SharePointClient

# Get logger for this module
logger = get_logger("llm_service")


class LLMService:
    """
    Enhanced LLM service with error handling, validation, and retry logic.
    """

    def __init__(self, model: str = None, host: str = None):
        """
        Initialize LLM service with optional configuration.

        Args:
            model: LLM model name (optional, uses config if not provided)
            host: LLM host URL (optional, uses config if not provided)

        Raises:
            LLMConnectionError: If LLM connection fails
        """
        self.llm: Optional[Ollama] = None
        self.agent = None
        self.memory: Optional[ConversationBufferMemory] = None
        self.is_connected = False
        self.connection_time: Optional[float] = None

        # Get configuration
        try:
            llm_config = config_manager.llm
            self.model = model or llm_config.model
            self.host = host or llm_config.host
            self.max_tokens = llm_config.max_tokens
            self.temperature = llm_config.temperature
            self.timeout = llm_config.timeout
        except Exception as e:
            logger.error(f"Failed to load LLM configuration: {e}")
            # Use defaults if config fails
            self.model = model or LLMConstants.DEFAULT_MODEL
            self.host = host or LLMConstants.DEFAULT_OLLAMA_HOST
            self.max_tokens = LLMConstants.MAX_TOKENS
            self.temperature = LLMConstants.TEMPERATURE
            self.timeout = LLMConstants.LLM_TIMEOUT

        # Initialize LLM and agent
        self._initialize_llm()
        self._create_agent()

    @log_function_call(logger)
    def _initialize_llm(self):
        """
        Initialize the LLM connection.

        Raises:
            LLMConnectionError: If LLM initialization fails
        """
        try:
            logger.info(f"Initializing LLM: {self.model} at {self.host}")

            with log_performance(logger, "LLM initialization"):
                # Create Ollama LLM instance
                self.llm = Ollama(
                    model=self.model,
                    base_url=self.host,
                    temperature=self.temperature,
                    timeout=self.timeout,
                )

                # Test connection with a simple query
                test_response = self.llm.invoke("Hello")

                if not test_response:
                    raise LLMConnectionError(
                        "LLM returned empty response during connection test"
                    )

                self.is_connected = True
                self.connection_time = time.time()

                logger.info(f"Successfully connected to LLM: {self.model}")

        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise LLMConnectionError(f"LLM initialization failed: {str(e)}")

    @log_function_call(logger)
    def _create_agent(self):
        """
        Create the LangChain agent with SharePoint tools.

        Raises:
            LLMConnectionError: If agent creation fails
        """
        try:
            logger.info("Creating LLM agent with SharePoint tools")

            # Create SharePoint client for tools
            sp_client = SharePointClient()

            # Define tools for the agent
            tools = self._create_tools(sp_client)

            # Create memory for conversation history
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                max_token_limit=LLMConstants.MAX_MEMORY_TOKENS,
                return_messages=True,
            )

            # Create system prompt
            system_prompt = self._create_system_prompt()

            # Create chat prompt template
            chat_prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

            # Initialize agent
            self.agent = initialize_agent(
                tools=tools,
                llm=self.llm,
                agent="zero-shot-react-description",
                memory=self.memory,
                verbose=True,
                max_iterations=3,  # Limit iterations to prevent infinite loops
                early_stopping_method="generate",
            )

            logger.info("Successfully created LLM agent")

        except Exception as e:
            logger.error(f"Failed to create LLM agent: {e}")
            raise LLMConnectionError(f"Agent creation failed: {str(e)}")

    def _create_tools(self, sp_client: SharePointClient) -> List[Tool]:
        """
        Create tools for the LLM agent.

        Args:
            sp_client: SharePoint client instance

        Returns:
            List of tools for the agent
        """

        def search_documents_tool(query: str) -> str:
            """Search SharePoint document libraries for files."""
            try:
                # Validate input
                validated_query = validate_user_input(query)

                # Search in default library
                df = sp_client.search_documents("Documents", validated_query)

                if df.empty:
                    return f"No documents found matching '{validated_query}'"

                # Format results as markdown
                result = f"Found {len(df)} documents matching '{validated_query}':\n\n"
                result += df.to_markdown(index=False)

                return result

            except Exception as e:
                logger.error(f"Error in search_documents_tool: {e}")
                return f"Error searching documents: {str(e)}"

        def list_sharepoint_items_tool(list_name: str = "Onboarding Checklist") -> str:
            """List items from a SharePoint list."""
            try:
                # Get items from the specified list
                df = sp_client.list_items(list_name)

                if df.empty:
                    return f"No items found in list '{list_name}'"

                # Format results as markdown
                result = f"Items from '{list_name}' list:\n\n"
                result += df.to_markdown(index=False)

                return result

            except Exception as e:
                logger.error(f"Error in list_sharepoint_items_tool: {e}")
                return f"Error listing items from '{list_name}': {str(e)}"

        def get_document_libraries_tool() -> str:
            """Get list of available document libraries."""
            try:
                libraries = sp_client.list_document_libraries()

                if not libraries:
                    return "No document libraries found"

                result = "Available document libraries:\n\n"
                for lib in libraries:
                    result += f"- **{lib['title']}**: {lib['description']} ({lib['item_count']} items)\n"

                return result

            except Exception as e:
                logger.error(f"Error in get_document_libraries_tool: {e}")
                return f"Error getting document libraries: {str(e)}"

        # Create tool list
        tools = [
            Tool(
                name="SearchDocuments",
                func=search_documents_tool,
                description="Search SharePoint document libraries for files by name. Use this when users ask about finding documents or files.",
            ),
            Tool(
                name="ListSharePointItems",
                func=list_sharepoint_items_tool,
                description="List items from SharePoint lists like 'Onboarding Checklist'. Use this when users ask about list items or checklist items.",
            ),
            Tool(
                name="GetDocumentLibraries",
                func=get_document_libraries_tool,
                description="Get a list of available document libraries in SharePoint. Use this when users ask what libraries are available.",
            ),
        ]

        return tools

    def _create_system_prompt(self) -> str:
        """
        Create the system prompt for the LLM agent.

        *** EDIT AGENT PROMPT HERE ***
        To customize the AI assistant's behavior, modify the prompt text below.
        You can also edit this through the UI in the "Agent Settings" section.

        Returns:
            System prompt string
        """
        # *** AGENT PROMPT CONFIGURATION ***
        # This is the main prompt that defines how the AI assistant behaves.
        # You can modify this text to change the assistant's personality,
        # capabilities, and response style.

        # Check if custom prompt exists in session state (from UI editor)
        if hasattr(self, "custom_prompt") and self.custom_prompt:
            return self.custom_prompt

        # Default system prompt - EDIT THIS TEXT TO CUSTOMIZE THE AGENT
        default_prompt = """
You are an expert SharePoint assistant with access to SharePoint document libraries and lists.

Your capabilities include:
- Searching for documents in SharePoint libraries
- Listing items from SharePoint lists
- Providing information about available document libraries
- Answering questions about SharePoint content

Guidelines:
1. Always be helpful, concise, and professional
2. When using tools, clearly reference the results in your response
3. If a tool returns an error, explain what went wrong and suggest alternatives
4. Provide specific, actionable information when possible
5. If you cannot find what the user is looking for, suggest alternative approaches

Remember to use the available tools to provide accurate, up-to-date information from SharePoint.
"""

        return default_prompt.strip()

    def update_system_prompt(self, new_prompt: str):
        """
        Update the system prompt for the LLM agent.

        Args:
            new_prompt: New system prompt text
        """
        # Store the custom prompt
        self.custom_prompt = new_prompt.strip()

        # Recreate the agent with the new prompt
        try:
            self._create_agent()
            logger.info("Successfully updated system prompt")
        except Exception as e:
            logger.error(f"Failed to update system prompt: {e}")
            raise LLMConnectionError(f"Failed to update system prompt: {str(e)}")

    def get_current_prompt(self) -> str:
        """
        Get the current system prompt.

        Returns:
            Current system prompt text
        """
        return self._create_system_prompt()

    def reset_prompt_to_default(self):
        """Reset the system prompt to default."""
        if hasattr(self, "custom_prompt"):
            delattr(self, "custom_prompt")
        self._create_agent()
        logger.info("Reset system prompt to default")

    @contextmanager
    def _handle_llm_errors(self, operation: str):
        """
        Context manager for handling LLM errors.

        Args:
            operation: Description of the operation being performed
        """
        try:
            yield
        except Exception as e:
            error_msg = str(e).lower()

            if "timeout" in error_msg or "timed out" in error_msg:
                logger.error(f"LLM timeout during {operation}: {e}")
                raise LLMTimeoutError(f"LLM request timed out during {operation}")
            elif "connection" in error_msg or "connect" in error_msg:
                logger.error(f"LLM connection error during {operation}: {e}")
                raise LLMConnectionError(f"LLM connection failed during {operation}")
            else:
                logger.error(f"LLM error during {operation}: {e}")
                raise LLMResponseError(f"LLM error during {operation}: {str(e)}")

    def _ensure_connected(self):
        """
        Ensure LLM is connected and ready.

        Raises:
            LLMConnectionError: If not connected
        """
        if not self.is_connected or not self.llm or not self.agent:
            raise LLMConnectionError("LLM not connected or agent not initialized")

    @log_function_call(logger)
    def run(self, user_input: str) -> str:
        """
        Process user input and return LLM response.

        Args:
            user_input: User's question or request

        Returns:
            LLM response string

        Raises:
            LLMConnectionError: If not connected
            LLMTimeoutError: If request times out
            LLMResponseError: If response is invalid
        """
        self._ensure_connected()

        # Validate input
        try:
            validated_input = validate_user_input(user_input, max_length=1000)
        except Exception as e:
            logger.warning(f"Input validation failed: {e}")
            return f"Invalid input: {str(e)}"

        try:
            with log_performance(logger, "LLM query processing"):
                with self._handle_llm_errors("processing user query"):
                    logger.info(f"Processing user query: {validated_input[:100]}...")

                    # Run the agent
                    response = self.agent.run(validated_input)

                    if not response:
                        logger.warning("LLM returned empty response")
                        return "I apologize, but I couldn't generate a response. Please try rephrasing your question."

                    logger.info(f"Generated response: {len(response)} characters")
                    return response

        except (LLMConnectionError, LLMTimeoutError, LLMResponseError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during LLM processing: {e}")
            raise LLMResponseError(f"Unexpected error: {str(e)}")

    @log_function_call(logger)
    def clear_memory(self):
        """Clear the conversation memory."""
        if self.memory:
            self.memory.clear()
            logger.info("Cleared conversation memory")

    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get summary of current conversation memory.

        Returns:
            Dictionary with memory information
        """
        if not self.memory:
            return {"messages": 0, "tokens": 0}

        try:
            messages = self.memory.chat_memory.messages
            return {
                "messages": len(messages),
                "tokens": sum(len(msg.content) for msg in messages),
                "buffer_size": len(str(self.memory.buffer)),
            }
        except Exception as e:
            logger.warning(f"Failed to get memory summary: {e}")
            return {"error": str(e)}

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the current LLM connection.

        Returns:
            Dictionary with connection information
        """
        return {
            "is_connected": self.is_connected,
            "model": self.model,
            "host": self.host,
            "connection_time": self.connection_time,
            "uptime_seconds": (
                time.time() - self.connection_time if self.connection_time else None
            ),
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
        }

    def disconnect(self):
        """Disconnect from LLM and clean up resources."""
        if self.memory:
            self.memory.clear()

        self.llm = None
        self.agent = None
        self.memory = None
        self.is_connected = False
        self.connection_time = None

        logger.info("Disconnected from LLM service")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def create_llm_agent() -> LLMService:
    """
    Factory function to create an LLM agent (for backward compatibility).

    Returns:
        LLMService instance
    """
    return LLMService()
