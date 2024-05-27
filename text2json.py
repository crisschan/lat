'''
@File    :   try_gradio.py
@Time    :   2024/04/12 01:02:06
@Author  :   CrissChan 
@Version :   1.0
@Site    :   https://blog.csdn.net/crisschan
@Desc    :   反馈参数
'''
from llama_index.core.node_parser import JSONNodeParser
from llama_index.core import Document
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import PromptTemplate
from chatglm import ChatGLM, ChatGLMEmbeddings
import requests
import json
from dotenv import load_dotenv, find_dotenv
import os

## 获取.env文件中的变量
_=load_dotenv(find_dotenv())

## 从env文件中调用chatglm
ZHIPU_API_KEY =os.getenv("ZHIPU_API_KEY")
model_id = os.getenv("MODEL_ID")
embed_model = os.getenv("EMBED_MODE")



class Text2JSon:
    # def __init__(self, url: str, http_method="GET"):
        
    def get_jsonfile(self,url: str, http_method="GET"):
          '''
          @des  :下载对应的json文件存储到本地文件中
          @params  :url swagger对应json的地址
                    http_method swagger的http访问方式
          '''
          
          
          self.url = url
          self.headers = {
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299",
              "content-Type": "application/json"
          }
          if http_method == "GET":
              response = requests.get(url=url, headers=self.headers)
          elif http_method == "POST":
              response = requests.post(url=url, headers=self.headers)
          else:
              raise Exception("http_method must be GET or POST")
          # self.response = response
          json_file = url.replace(":",".").replace("/","_")+'.json'
          with open(json_file, 'w') as f:
              f.write(response.text)
          return json_file
    def is_json_string(self,s):
        '''
        @des  :判断是不是json
        @params  : s 需要判断的字符串
        '''
        try:
            # 尝试解析JSON
            json.loads(s)
            return True
        except json.JSONDecodeError:
            # 如果解析失败，则返回False
            return False
    def query_engine(self,json_file:str):
        '''
        @des  : 查询引擎，传入json文件后生成接口测试代码
        @params  : json_file 需要传入的json文件（swagger模式）
        '''
        self.node_parser = JSONNodeParser()
        # text2json
        # ## chatglm modle
        Settings.llm = ChatGLM(
            model=model_id, reuse_client=True, api_key=ZHIPU_API_KEY,)
        # llm = ChatGLM(model=model_id, reuse_client=True, api_key=ZHIPU_API_KEY,)
        # ## chatglm的embedding model

        Settings.embed_model = ChatGLMEmbeddings(
            model=embed_model, reuse_client=True, api_key=ZHIPU_API_KEY,)
        with open(json_file, 'r') as f:
            text=f.read()
            if self.is_json_string(text):
                document = Document(id_=json_file, text=text)
                parser = JSONNodeParser()
                nodes = parser.get_nodes_from_documents([document])
                index = VectorStoreIndex(nodes)
                # BM25（Best Matching 25）是一种用于信息检索（IR）的经典算法，用于评估文档与查询之间的相关性。
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
                with open("prompt_template_pytest_api.txt", "r") as file:
                    PROMPT_TEMPLATE_STR = file.read()
                prompt_template = PromptTemplate(PROMPT_TEMPLATE_STR)
                      # text_qa_template 这指的是一个用于文本问答（Text Question Answering, 简称 QA）任务的模板
                query_engine.update_prompts(
                    {"response_synthesizer:text_qa_template": prompt_template}
                    )
            else:
                raise  Exception("response text is not json")

        return query_engine


if __name__ == '__main__':
    
    t2j = Text2JSon()
    # filename= t2j.get_jsonfile(url="https://petstore3.swagger.io/api/v3/openapi.json")
    filename="pet.json"
    qe = t2j.query_engine(filename)
    query_str = (
                "完成pet接口put和post方法的测试脚本的开发，测试脚本参数以及参数取值放到param_list中，接口测试脚本的base url是https://petstore3.swagger.io/api/v3，"
                 )
    res = qe.query(query_str)
    print(res)
