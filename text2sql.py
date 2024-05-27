#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   text2sql.py
@Time    :   2024/04/10 00:39:28
@Author  :   CrissChan 
@Version :   1.0
@Site    :   https://blog.csdn.net/crisschan
@Desc    :   文本2sql
'''
from enum import Enum
from sqlalchemy import (
    create_engine,
)

from llama_index.core import SQLDatabase
from chatglm import ChatGLM,ChatGLMEmbeddings
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core import Settings
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core import VectorStoreIndex
from llama_index.core.indices.struct_store.sql_query import (
    SQLTableRetrieverQueryEngine,
)
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from dotenv import load_dotenv, find_dotenv
import os

## 获取.env文件中的变量
_=load_dotenv(find_dotenv())

## 从env文件中调用chatglm
ZHIPU_API_KEY =os.getenv("ZHIPU_API_KEY")
model_id = os.getenv("MODEL_ID")
embed_model = os.getenv("EMBED_MODE")


class QueryEngineType(Enum):
    #默认Query Engine就是之间建立一个数据库相关的向量数据，进行查询,侧重于直接转换和精确映射
    #它能够将用户的自然语言查询转换为SQL查询。Query Engine需要理解用户的查询意图，并将其映射到数据库模式中相应的表格和字段。
    #这种方法可能包括自然语言处理（NLP）技术，如词法分析、句法分析和语义解析，以确保生成的SQL语句准确无误。
    #Query Engine的目标是提供一个高效、准确的查询转换服务，用户可以直接与其交互，输入自然语言查询并得到SQL查询结果。
    DEFAULT = 1
    # Query-Time Retrieval of Tables ,强调查询时的动态表格选择
    #这种方法强调在查询执行时才确定和检索需要使用的表格。这可能意味着系统在用户提出查询时，首先分析查询内容，然后动态地从数据库中检索和查询相关的表格。
    #这种方法可能更加灵活，因为它允许系统根据实际的查询需求来选择数据源，而不是依赖于预定义的模式。
    #这种方法可能对于用户不熟悉数据库结构或者查询需求不明确的情况特别有用。
    QUERYTIME = 2
    # 建立一个Retirver，然后在进行查找
    # Retriever方法可能指的是一种基于检索的系统，它通过搜索和匹配已有的SQL查询模板或模式来响应用户的自然语言查询。
    # 当用户提出查询时，系统会在库中寻找最接近的匹配项，并将其作为响应。
    # Retriever方法的优点在于可以快速响应用户的查询，但它的准确性和适用性可能受限于templete的覆盖范围和质量。
    RETRIVER = 3

class Text2SQL(object):
    def __init__(self,db_engine,include_tables:list=None,type=QueryEngineType.DEFAULT) -> None:
        self.db_engine = db_engine
        # self.include_tables = include_tables
        self.type = type
        if include_tables is None:
            self.sql_database = SQLDatabase( self.db_engine)
        else:
            self.sql_database = SQLDatabase( self.db_engine, include_tables=include_tables)
        pass
    
    def query_engine(self,include_tables:list=None):
        '''
        @des  : 查询引擎
        @params  :include_tables需要传入的表名，如果说选择了QUERYTIME模式，那么只能传入一个表名
        '''
        ## text2sql
        # ## chatglm modle
        Settings.llm = ChatGLM(model=model_id, reuse_client=True, api_key=ZHIPU_API_KEY,)
        # llm = ChatGLM(model=model_id, reuse_client=True, api_key=ZHIPU_API_KEY,)
        # ## chatglm的embedding model
        
        Settings.embed_model = ChatGLMEmbeddings(model=embed_model, reuse_client=True, api_key=ZHIPU_API_KEY,)

        if self.type == QueryEngineType.DEFAULT:
        
            if include_tables is None:
                query_engine = NLSQLTableQueryEngine(
                    sql_database=self.sql_database
                )
            else:
                query_engine = NLSQLTableQueryEngine(
                    sql_database=self.sql_database, tables=include_tables
                )
        elif self.type == QueryEngineType.QUERYTIME:
            if include_tables is None:
                raise Exception("QueryTime need one table")
            elif len(include_tables) != 1:
                raise Exception("QueryTime need one table")
            table_node_mapping = SQLTableNodeMapping(self.sql_database)
            #############SQLTableSchema可以接受context_str参数，这个参数可以自定义一些schema，例如可以说吗，case代表case_name字段等内容
            table_schema_objs = [
                (SQLTableSchema(table_name=include_tables[0]))
            ] 
            obj_index = ObjectIndex.from_objects(
                table_schema_objs,
                table_node_mapping,
                VectorStoreIndex,
            )
            query_engine = SQLTableRetrieverQueryEngine(
                self.sql_database, obj_index.as_retriever(similarity_top_k=1)
            )
        elif self.type == QueryEngineType.RETRIVER:
            nl_sql_retriever = NLSQLRetriever(
            self.sql_database, tables=include_tables,return_raw=True
            )
            query_engine = RetrieverQueryEngine.from_args(nl_sql_retriever)
        else:
            raise Exception("Unkown QueryEngineType")
        return query_engine 
if __name__ == '__main__':
    # "sqlite:///:memory:": 这是一个数据库 URL，指定了数据库类型（SQLite）、连接信息等。在这个例子中，
    #sqlite 表示使用 SQLite 数据库，:memory: 表示数据库将存在于内存中，而不是在磁盘上的一个文件。这意味着数据库是临时的，当程序结束时，所有的数据都会丢失。
    #engine = create_engine("sqlite:///:memory:")
    #例子只用已经在磁盘目录的tsdb.db
    engine = create_engine("sqlite:///database/petstore.db")
    # metadata_obj = MetaData()
    # Base = declarative_base()
    
    t2sql = Text2SQL(engine,include_tables=["pets","category","order","user"],type=QueryEngineType.DEFAULT)
    format_str = '{"$schema": "http://json-schema.org/schema#",  "title": "Pet",  "type": "object",  "properties": {    "id": {      "type": "integer",      "description": "The unique identifier of the pet."    },    "name": {      "type": "string",      "description": "The name of the pet."    },    "category": {      "type": "object",      "properties": {        "id": {          "type": "integer",          "description": "The unique identifier of the pet category."        }      },      "required": ["id"],      "description": "The category of the pet."    },    "status": {      "type": "string",      "enum": ["available", "pending", "sold"],      "description": "The status of the pet."    }  },  "required": ["id", "name", "category", "status"],  "description": "A representation of a pet with its details."}'
    # format_str = "param_list = [ {'method': 'put', 'endpoint': '/pet', 'data': {'id': , 'name': '', 'status': ''}, 'expected_status': 200},{'method': 'post', 'endpoint': '/pet', 'data': {'': '', 'status': ''}, 'expected_status': 201},]"
    query_str = (
                 f"请帮我生成10条数据，数据格式按照{format_str}的schema，并按照json格式返回给我"
                )
             
    qe = t2sql.query_engine(include_tables=["pets","category","order","user"])
    res = qe.query(query_str)
    print(res)
