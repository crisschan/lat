#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   chatglm.py
@Time    :   2024/03/19 23:06:52
@Author  :   CrissChan 
@Version :   1.0
@Site    :   https://blog.csdn.net/crisschan
@Desc    :   按照Llama Index的文档，自定义一个ChatGLM继承CutomLLM，并且封装了ChatGLMEmbedding,对于模型的response的内容做了只针对代码部分的处理。
'''


from typing import Optional, List, Mapping, Any, Sequence, Dict
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core.constants import DEFAULT_CONTEXT_WINDOW, DEFAULT_NUM_OUTPUTS
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
    ChatMessage,
    ChatResponse,
)
from llama_index.core.llms.callbacks import llm_completion_callback, llm_chat_callback
from typing import Any, List
from llama_index.core.embeddings import BaseEmbedding
from zhipuai import ZhipuAI

DEFAULT_MODEL = 'glm-4'

def to_message_dicts(messages: Sequence[ChatMessage])->List:
    return [
        {"role": message.role.value, "content": message.content,} 
                for message in messages if all([value is not None for value in message.values()])
    ]

def get_additional_kwargs(response) -> Dict:
    return {
        "token_counts":response.usage.total_tokens,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
    }

class ChatGLM(CustomLLM):
    num_output: int = DEFAULT_NUM_OUTPUTS
    context_window: int = Field(default=DEFAULT_CONTEXT_WINDOW,description="The maximum number of context tokens for the model.",gt=0,)
    model: str = Field(default=DEFAULT_MODEL, description="The ChatGlM model to use. glm-4 or glm-3-turbo")
    api_key: str = Field(default=None, description="The ChatGLM API key.")
    reuse_client: bool = Field(default=True, description=(
            "Reuse the client between requests. When doing anything with large "
            "volumes of async API calls, setting this to false can improve stability."
        ),
    )

    _client: Optional[Any] = PrivateAttr()
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        reuse_client: bool = True,
        api_key: Optional[str] = None,
        **kwargs: Any,
    )-> None:
        super().__init__(
            model=model,
            api_key=api_key,
            reuse_client=reuse_client,
            **kwargs,
        )
        self._client = None

    def _get_client(self) -> ZhipuAI:
        if not self.reuse_client :
            return ZhipuAI(api_key=self.api_key)

        if self._client is None:
            self._client = ZhipuAI(api_key=self.api_key)
        return self._client

    @classmethod
    def class_name(cls) -> str:
        return "chatglm_llm"

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model,
        )

    def _chat(self, messages:List, stream=False) -> Any:
        #print("--------------------------------------------")
        #import traceback
        #s=traceback.extract_stack()
        # print("%s %s invoke _chat" % (s[-2],s[-2][2]))
        # print(messages)
        # print("--------------------------------------------")
        response = self._get_client().chat.completions.create(
            model=self.model,  # 填写需要调用的模型名称
            messages=messages,
        )
        # print(f"_chat, response: {response}")
        return response

    #@llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        message_dicts: List = to_message_dicts(messages)
        response = self._chat(message_dicts, stream=False)
        # print(f"chat: {response} ")
        rsp = ChatResponse(
            message=ChatMessage(content=response.choices[0].message.content, role=MessageRole(response.choices[0].message.role),
                additional_kwargs= {}),
            raw=response, additional_kwargs= get_additional_kwargs(response),
        )
        print(f"chat: {rsp} ")

        return rsp

    #@llm_chat_callback()
    def stream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> CompletionResponseGen:
        response_txt = ""
        message_dicts: List = to_message_dicts(messages)
        response = self._chat(message_dicts, stream=True)
        # print(f"stream_chat: {response} ")
        for chunk in response:
            # chunk.choices[0].delta # content='```' role='assistant' tool_calls=None
            token = chunk.choices[0].delta.content
            response_txt += token
            yield ChatResponse(message=ChatMessage(content=response_txt,role=MessageRole(message.get("role")),
                                additional_kwargs={},), delta=token, raw=chunk,)

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        messages = [{"role": "user", "content": prompt}]
        # print(f"complete: messages {messages} ")
        try:
            response = self._chat(messages, stream=False)

            rsp = CompletionResponse(text=str(response.choices[0].message.content), 
                                     raw=response, 
                                     additional_kwargs=get_additional_kwargs(response),)
            # print(f"complete: {rsp} ")
        except Exception as e:
            print(f"complete: exception {e}")

        return rsp

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        response_txt = ""
        messages = [{"role": "user", "content": prompt}]
        response = self._chat(messages, stream=True)
        # print(f"stream_complete: {response} ")
        # print(f"stream_content: {response.choices[0].message.content} ")
        # i= 0
        # yield CompletionResponse(text=response.choices[0].message.content, delta=response.choices[0].message)

        for chunk in response.choices[0].message.content.splitlines():
            # chunk.choices[0].delta # content='```' role='assistant' tool_calls=None
            # print(f"stream chunk :{chunk}")
            
            try:
          
                token = chunk+"\r\n"
             
            except:
                print(f"stream exception :{chunk}")
                continue
                

            response_txt += token
            # print(f"token{i}: {token} ")
            # i=i+1
            yield CompletionResponse(text=response_txt, delta=token)
# ZHIPU_API_KEY="d9b0b2de5ce4a9774f02220127e71f42.Km7pms8NSzqDuS4a"
# test_llm = ChatGLM(model='glm-4', reuse_client=True, api_key=ZHIPU_API_KEY,)
# test_messages = [{"role": "user", "content": "你好啊"}]
# response = test_llm._chat(test_messages)
# print(response.choices[0].message)

# Completion(model='glm-4', created=1709175132, choices=[CompletionChoice(index=0, finish_reason='stop', message=CompletionMessage(content='你好！有什么可以帮助你的吗？如果有任何问题或需要咨询的事情，请随时告诉我。', role='assistant', tool_calls=None))], request_id='8434491822902510320', id='8434491822902510320', usage=CompletionUsage(prompt_tokens=7, completion_tokens=21, total_tokens=28))
# test_messages=[{'role': 'user', 'content': 'Context information is below.\n---------------------\n小白龙的大哥是孙悟空\n\n今天天气不错\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: 小白龙的大哥是谁\nAnswer: '}]
# test_llm._chat(test_messages)
# Completion(model='glm-4', created=1709175133, choices=[CompletionChoice(index=0, finish_reason='stop', message=CompletionMessage(content='孙悟空。根据您提供的信息，“小白龙的大哥是孙悟空”。所以在这一语境中，答案是孙悟空。', role='assistant', tool_calls=None))], request_id='8434486222265024571', id='8434486222265024571', usage=CompletionUsage(prompt_tokens=50, completion_tokens=24, total_tokens=74))
# # test_llm.chat(test_messages)
            



class ChatGLMEmbeddings(BaseEmbedding):
    model: str = Field(default='embedding-2', description="The ChatGlM model to use. embedding-2")
    api_key: str = Field(default=None, description="The ChatGLM API key.")
    reuse_client: bool = Field(default=True, description=(
            "Reuse the client between requests. When doing anything with large "
            "volumes of async API calls, setting this to false can improve stability."
        ),
    )

    _client: Optional[Any] = PrivateAttr()
    def __init__(
        self,
        model: str = 'embedding-2',
        reuse_client: bool = True,
        api_key: Optional[str] = None,
        **kwargs: Any,
    )-> None:
        super().__init__(
            model=model,
            api_key=api_key,
            reuse_client=reuse_client,
            **kwargs,
        )
        self._client = None

    def _get_client(self) -> ZhipuAI:
        if not self.reuse_client :
            return ZhipuAI(api_key=self.api_key)

        if self._client is None:
            self._client = ZhipuAI(api_key=self.api_key)
        return self._client

    @classmethod
    def class_name(cls) -> str:
        return "ChatGLMEmbedding"

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get query embedding."""
        return self.get_general_text_embedding(query)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """The asynchronous version of _get_query_embedding."""
        return self.get_general_text_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        return self.get_general_text_embedding(text)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Asynchronously get text embedding."""
        return self.get_general_text_embedding(text)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get text embeddings."""
        embeddings_list: List[List[float]] = []
        for text in texts:
            embeddings = self.get_general_text_embedding(text)
            embeddings_list.append(embeddings)

        return embeddings_list

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get text embeddings."""
        return self._get_text_embeddings(texts)

    def get_general_text_embedding(self, prompt: str) -> List[float]:
        response = self._get_client().embeddings.create(
            model=self.model, #填写需要调用的模型名称
            input=prompt,
        )
        return response.data[0].embedding
    


# if __name__ == '__main__':
#     ZHIPU_API_KEY="d9b0b2de5ce4a9774f02220127e71f42.Km7pms8NSzqDuS4a"
#     test_embedding = ChatGLMEmbeddings(model='embedding-2', reuse_client=True, api_key=ZHIPU_API_KEY,)
#     test_embedding.get_general_text_embedding('test')[:5]
#     [-0.01880447380244732,
#     0.04475865885615349,
#     -0.0690813660621643,
#     -0.03967287391424179,
#     0.030761191621422768]