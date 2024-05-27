'''
@File    :   try_gradio.py
@Time    :   2024/04/12 03:02:06
@Author  :   CrissChan 
@Version :   1.0
@Site    :   https://blog.csdn.net/crisschan
@Desc    :   生成python的pytest的代码
'''
from llama_index.core.node_parser import CodeSplitter
from llama_index.core import Document
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import PromptTemplate
from chatglm import ChatGLM, ChatGLMEmbeddings
from dotenv import load_dotenv, find_dotenv
import os

## 获取.env文件中的变量
_=load_dotenv(find_dotenv())

## 从env文件中调用chatglm
ZHIPU_API_KEY =os.getenv("ZHIPU_API_KEY")
model_id = os.getenv("MODEL_ID")
embed_model = os.getenv("EMBED_MODE")


class Text2Python:
    
    def query_engine(self,python_code:str):
        Settings.llm = ChatGLM(model=model_id, reuse_client=True, api_key=ZHIPU_API_KEY)
        Settings.embed_model = ChatGLMEmbeddings(model=embed_model, reuse_client=True, api_key=ZHIPU_API_KEY)
       
        text_list = [python_code]
        documents = [Document(text=t) for t in text_list]

        splitter = CodeSplitter(
            language="python",
            chunk_lines=40,  # lines per chunk
            chunk_lines_overlap=200,  # lines overlap between chunks
            max_chars=1500,  # max chars per chunk
        )
        nodes = splitter.get_nodes_from_documents(documents)
        nodes = [node for node in nodes if node.text]
        # 
        index = VectorStoreIndex(nodes)
        retriever = BM25Retriever.from_defaults(
                    index=index,
                    similarity_top_k=3,
                )

        response_synthesizer = get_response_synthesizer(streaming=True)
        # assemble query engine
        # we can plug our retriever into a query engine to synthesize natural language responses.
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )
        #  with open("prompt_template_pytest_api.txt", "r") as file:
        #             PROMPT_TEMPLATE_STR = file.read()
        #         prompt_template = PromptTemplate(PROMPT_TEMPLATE_STR)
        #               # text_qa_template 这指的是一个用于文本问答（Text Question Answering, 简称 QA）任务的模板
        #         query_engine.update_prompts(
        #             {"response_synthesizer:text_qa_template": prompt_template}
        #             )
        return query_engine

if __name__ == '__main__':
    cf="""import requests
import pytest

base_url = "https://petstore3.swagger.io/api/v3"

# Parameters for the test cases
param_list = [
    # For POST method
    {
        "url": base_url + "/pet",
        "method": "post",
        "headers": {"Content-Type": "application/json"},
        "data": '{"id": 1, "name": "TestPet", "category": {"id": 1}, "status": "available"}',
        "expected_status": 200,
        "expected_length": 1
    },
    # For PUT method
    {
        "url": base_url + "/pet",
        "method": "put",
        "headers": {"Content-Type": "application/json"},
        "data": '{"id": 1, "name": "UpdatedTestPet", "category": {"id": 1}, "status": "sold"}',
        "expected_status": 200,
        "expected_length": 1
    }
]

# Test function for the API requests
@pytest.mark.parametrize("param", param_list)
def test_pet_api(param):
    if param["method"] == "post":
        response = requests.post(param["url"], headers=param["headers"], data=param["data"])
    elif param["method"] == "put":
        response = requests.put(param["url"], headers=param["headers"], data=param["data"])
    else:
        raise ValueError("Unsupported HTTP method")

    # Assert response code
    assert response.status_code == param["expected_status"]

    # Assert response JSON length (assuming that the response is a JSON list)
    try:
        response_json = response.json()
        assert len(response_json) == param["expected_length"]
    except Exception as e:
        pytest.fail("Failed to assert response JSON length: " + str(e))"""
    t2p=Text2Python()
    qe =t2p.query_engine(cf)
    res = qe.query("param_list中request body是那部分数据")
    print(res)