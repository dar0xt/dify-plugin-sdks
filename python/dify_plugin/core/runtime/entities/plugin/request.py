from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from dify_plugin.core.runtime.entities.model_runtime.message import AssistantPromptMessage, PromptMessage, PromptMessageRole, PromptMessageTool, SystemPromptMessage, ToolPromptMessage, UserPromptMessage
from dify_plugin.model.model_entities import ModelType

class PluginInvokeType(Enum):
    Tool = 'tool'
    Model = 'model'

class ToolActions(Enum):
    ValidateCredentials = 'validate_credentials'
    Invoke = 'invoke'

class ModelActions(Enum):
    ValidateProviderCredentials = 'validate_provider_credentials'
    ValidateModelCredentials = 'validate_model_credentials'
    InvokeLLM = 'invoke_llm'
    InvokeTextEmbedding = 'invoke_text_embedding'
    InvokeRerank = 'invoke_rerank'
    InvokeTTS = 'invoke_tts'
    InvokeSpeech2Text = 'invoke_speech2text'
    InvokeModeration = 'invoke_moderation'

class PluginAccessRequest(BaseModel):
    type: PluginInvokeType
    user_id: str

class ToolInvokeRequest(PluginAccessRequest):
    type: PluginInvokeType = PluginInvokeType.Tool
    action: ToolActions = ToolActions.Invoke
    provider: str
    tool: str
    credentials: dict
    parameters: dict[str, Any]

class ToolValidateCredentialsRequest(PluginAccessRequest):
    type: PluginInvokeType = PluginInvokeType.Tool
    action: ToolActions = ToolActions.ValidateCredentials
    provider: str
    credentials: dict

class PluginAccessModelRequest(BaseModel):
    type: PluginInvokeType = PluginInvokeType.Model
    user_id: str

class ModelInvokeLLMRequest(PluginAccessModelRequest):
    action: ModelActions = ModelActions.InvokeLLM
    provider: str
    model_type: ModelType
    model: str
    credentials: dict
    model_parameters: dict[str, Any]
    prompt_messages: list[PromptMessage]
    stop: Optional[list[str]]
    tools: Optional[list[PromptMessageTool]]
    stream: bool = True

    model_config = ConfigDict(protected_namespaces=())

    @field_validator('prompt_messages', mode='before')
    def convert_prompt_messages(cls, v):
        if not isinstance(v, list):
            raise ValueError('prompt_messages must be a list')
        
        for i in range(len(v)):
            if v[i]['role'] == PromptMessageRole.USER.value:
                v[i] = UserPromptMessage(**v[i])
            elif v[i]['role'] == PromptMessageRole.ASSISTANT.value:
                v[i] = AssistantPromptMessage(**v[i])
            elif v[i]['role'] == PromptMessageRole.SYSTEM.value:
                v[i] = SystemPromptMessage(**v[i])
            elif v[i]['role'] == PromptMessageRole.TOOL.value:
                v[i] = ToolPromptMessage(**v[i])
            else:
                v[i] = PromptMessage(**v[i])

        return v

class ModelValidateProviderCredentialsRequest(PluginAccessModelRequest):
    action: ModelActions = ModelActions.ValidateProviderCredentials
    provider: str
    credentials: dict

class ModelValidateModelCredentialsRequest(PluginAccessModelRequest):
    action: ModelActions = ModelActions.ValidateModelCredentials
    provider: str
    model: str
    credentials: dict
