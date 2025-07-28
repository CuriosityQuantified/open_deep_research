from pydantic import BaseModel, Field
from typing import Any, List, Optional
from langchain_core.runnables import RunnableConfig
import os
from enum import Enum

class SearchAPI(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    TAVILY = "tavily"
    NONE = "none"

class MCPConfig(BaseModel):
    url: Optional[str] = Field(
        default=None,
        optional=True,
    )
    """The URL of the MCP server"""
    tools: Optional[List[str]] = Field(
        default=None,
        optional=True,
    )
    """The tools to make available to the LLM"""
    auth_required: Optional[bool] = Field(
        default=False,
        optional=True,
    )
    """Whether the MCP server requires authentication"""

class Configuration(BaseModel):
    # General Configuration
    max_structured_output_retries: int = Field(
        default=3,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "default": 3,
                "min": 1,
                "max": 10,
                "description": "Maximum number of retries for structured output calls from models"
            }
        }
    )
    allow_clarification: bool = Field(
        default=True,
        metadata={
            "x_oap_ui_config": {
                "type": "boolean",
                "default": True,
                "description": "Whether to allow the researcher to ask the user clarifying questions before starting research"
            }
        }
    )
    max_concurrent_research_units: int = Field(
        default=5,
        metadata={
            "x_oap_ui_config": {
                "type": "slider",
                "default": 5,
                "min": 1,
                "max": 20,
                "step": 1,
                "description": "Maximum number of research units to run concurrently. This will allow the researcher to use multiple sub-agents to conduct research. Note: with more concurrency, you may run into rate limits."
            }
        }
    )
    # Research Configuration
    search_api: SearchAPI = Field(
        default=SearchAPI.TAVILY,
        metadata={
            "x_oap_ui_config": {
                "type": "select",
                "default": "tavily",
                "description": "Search API to use for research.",
                "options": [
                    {"label": "Tavily", "value": SearchAPI.TAVILY.value},
                    {"label": "None", "value": SearchAPI.NONE.value}
                ]
            }
        }
    )
    max_researcher_iterations: int = Field(
        default=3,
        metadata={
            "x_oap_ui_config": {
                "type": "slider",
                "default": 3,
                "min": 1,
                "max": 10,
                "step": 1,
                "description": "Maximum number of research iterations for the Research Supervisor. This is the number of times the Research Supervisor will reflect on the research and ask follow-up questions."
            }
        }
    )
    max_react_tool_calls: int = Field(
        default=5,
        metadata={
            "x_oap_ui_config": {
                "type": "slider",
                "default": 5,
                "min": 1,
                "max": 30,
                "step": 1,
                "description": "Maximum number of tool calling iterations to make in a single researcher step."
            }
        }
    )
    # Custom Model Configuration - Summarization Model
    summarization_model_name: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "Model name for summarizing search results (e.g., 'gpt-4-turbo')"
            }
        }
    )
    summarization_model_base_url: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "Base URL for summarization model API endpoint"
            }
        }
    )
    summarization_model_api_key: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "API key for summarization model"
            }
        }
    )
    summarization_model_max_tokens: int = Field(
        default=4096,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "default": 4096,
                "description": "Maximum output tokens for summarization model"
            }
        }
    )
    
    # Custom Model Configuration - Research Model
    research_model_name: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "Model name for conducting research (e.g., 'claude-3-opus')"
            }
        }
    )
    research_model_base_url: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "Base URL for research model API endpoint"
            }
        }
    )
    research_model_api_key: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "API key for research model"
            }
        }
    )
    research_model_max_tokens: int = Field(
        default=8192,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "default": 8192,
                "description": "Maximum output tokens for research model"
            }
        }
    )
    
    # Custom Model Configuration - Compression Model
    compression_model_name: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "Model name for compressing research findings (e.g., 'gpt-4-turbo')"
            }
        }
    )
    compression_model_base_url: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "Base URL for compression model API endpoint"
            }
        }
    )
    compression_model_api_key: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "API key for compression model"
            }
        }
    )
    compression_model_max_tokens: int = Field(
        default=4096,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "default": 4096,
                "description": "Maximum output tokens for compression model"
            }
        }
    )
    
    # Custom Model Configuration - Final Report Model
    final_report_model_name: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "Model name for writing final report (e.g., 'claude-3-opus')"
            }
        }
    )
    final_report_model_base_url: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "Base URL for final report model API endpoint"
            }
        }
    )
    final_report_model_api_key: str = Field(
        default="",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "API key for final report model"
            }
        }
    )
    final_report_model_max_tokens: int = Field(
        default=16384,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "default": 16384,
                "description": "Maximum output tokens for final report model"
            }
        }
    )
    # MCP server configuration
    mcp_config: Optional[MCPConfig] = Field(
        default=None,
        optional=True,
        metadata={
            "x_oap_ui_config": {
                "type": "mcp",
                "description": "MCP server configuration"
            }
        }
    )
    mcp_prompt: Optional[str] = Field(
        default=None,
        optional=True,
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "description": "Any additional instructions to pass along to the Agent regarding the MCP tools that are available to it."
            }
        }
    )


    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = config.get("configurable", {}) if config else {}
        field_names = list(cls.model_fields.keys())
        values: dict[str, Any] = {
            field_name: os.environ.get(field_name.upper(), configurable.get(field_name))
            for field_name in field_names
        }
        return cls(**{k: v for k, v in values.items() if v is not None})

    class Config:
        arbitrary_types_allowed = True