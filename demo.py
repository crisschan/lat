#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   try_gradio.py
@Time    :   2024/04/12 23:02:06
@Author  :   CrissChan 
@Version :   1.0
@Site    :   https://blog.csdn.net/crisschan
@Desc    :   None
'''

import gradio as gr
from text2json import Text2JSon
from text2sql import Text2SQL,QueryEngineType
from text2python import Text2Python
from exec_text import ExecText
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
)
from chatglm import ChatGLM
import json
from dotenv import load_dotenv, find_dotenv
import os
# import sys
# from logger_stdio import Logger
from datetime import datetime
import subprocess


## 获取.env文件中的变量
_=load_dotenv(find_dotenv())

## 从env文件中调用chatglm
ZHIPU_API_KEY =os.getenv("ZHIPU_API_KEY")
model_id = os.getenv("MODEL_ID")
embed_model = os.getenv("EMBEDDING_MODEL")

# 全局
json_infor=""

def generate_testcase(json_infor,query_str):
    t2j = Text2JSon()
    qe_api = t2j.query_engine(json_infor)
    query_str_api = (
                query_str
                 )
    res_api= qe_api.query(query_str_api)
    
    gen_test_code = "#"+str(res_api).split("```")[1]
    return gen_test_code
def splite_requestbody(gen_test_code):
    # et = ExecText(gen_test_code)
    try:
        t2p=Text2Python()
        qe =t2p.query_engine(gen_test_code)
        res_param_list = qe.query("返回代码中的param_list")
        param_list= "#"+str(res_param_list).split("```")[1]

        request_body = qe.query("返回param_list中request body是那部分数据")
        request_body = "#"+str(request_body).split("```")[1]
        if request_body.find("{")!=0:
            request_body=request_body[request_body.find("{"):]
        return param_list,request_body
    except Exception as e:
        return "",""
def gen_requestboduy_shcema(request_body):
    # gen the request body json's schema
    try:
        test_llm = ChatGLM(model='glm-4', reuse_client=True, api_key=ZHIPU_API_KEY,)
        test_messages = [{"role": "user", "content": f"帮我生成{request_body}的json schema"}]
        res_json_schema = test_llm._chat(test_messages)
        json_schema_code = "#"+str(res_json_schema.choices[0].message.content).split("```")[1]
        request_body_schema=json_schema_code[json_schema_code.find('\n'):]
        return request_body_schema
    except Exception as e:
        return ""

def gen_testdata(db_infor,tables,request_body_schema):
    try:
        engine = create_engine(db_infor)
    
        t2sql = Text2SQL(engine,include_tables=json.loads(tables),type=QueryEngineType.DEFAULT)
        query_str_db = (
                    f"请帮我生成几条条数据，数据格式按照{request_body_schema}的schema，并按照json格式返回给我"
                    )
        qe_db = t2sql.query_engine(include_tables=["pets","category","order","user"])
        res_db = qe_db.query(query_str_db)
        test_data = "#"+str(res_db).split("```")[1]
        return test_data
    except Exception as e:
        return ""
def get_final_test_code(gen_test_code,request_body,param_list,test_data):
    try:
        et = ExecText(gen_test_code)
        final_test_code = et.replace_gen_code("\n"+request_body,param_list,test_data)
    except Exception as e:
        final_test_code = gen_test_code
    if final_test_code.find("__name__ ==") == -1:
        main_code_str="""\n
if __name__ == '__main__':\n
    args = ['--report=report.html',
        '--title=测试报告',
        '--tester=测试员',
        '--desc=报告描述信息',
        '--template=1']
    pytest.main(args)
"""
        final_test_code = final_test_code + main_code_str
    return final_test_code

def run_test(final_test_code):
    
    try:
        # 获取当前时间
        now = datetime.now()
        # # 获取当前时间的时间戳
        # timestamp = now.timestamp()
        gen_code_file_name = now.strftime("%Y%m%d%H%M%S")
        test_case_file =f"./at_testcase/test_autogen{gen_code_file_name}.py"
        with open(test_case_file, "w") as file:
            file.write(final_test_code)
        #2024-4-15 将exec 修改成subprocess完成测试case执行，report换成pytest-html最原始的样式
        
        command = ["pytest", f"./at_testcase/test_autogen{gen_code_file_name}.py",f"--html=./report/report{gen_code_file_name}.html","--self-contained-html"]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # # 获取标准输出和标准错误输出
        # print("STDOUT:", result.stdout)
        # print("STDERR:", result.stderr)

        # 检查命令是否执行成功
        # if result.returncode == 0:
        #     print("Command executed successfully")
        # else:
            # print("Command failed to execute")
        # 2024-4-15 后续为了保留页面的debug类信息，保留了exec执行，因此用平台每个生成的代码会有两次执行。
        # exec(final_test_code)
        # 设置要遍历的文件夹路径
        # folder_path = './debug'

        # 获取文件夹下的所有文件和文件夹的路径
        # entries = os.listdir(folder_path)

        # 过滤出所有文件，排除子文件夹
        # files = [os.path.join(folder_path, entry) for entry in entries if os.path.isfile(os.path.join(folder_path, entry))]

        # 按照文件的创建时间排序
        # sorted_files = sorted(files, key=lambda x: os.path.getctime(x),reverse=True)
        report_file=f"./report/report{gen_code_file_name}.html"
        try:
            # report_file=sorted_files[0]
            if len(result.stderr)>0:
                output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            else:
                output = f"STDOUT:\n{result.stdout}"
        # print("STDERR:", result.stderr)
            
            # with open(report_file, "r") as file:
            #     output = file.read()
        except Exception as e:
            output = f"Error in code execution: {str(e)}"
        return output,report_file,test_case_file

    except Exception as e:
        output = f"Error in code execution: {str(e)}"
        return output,None,None

def upload_file(uploaded_file):
    # 这里可以根据需要处理文件，例如读取内容、分析文件等
    if uploaded_file is not None:
        return uploaded_file
    else:
        return "没有上传文件"

html_title = """
<div align="center">
  <h1>AutoTester</h1>
  <p>AutoTester is a demo for Text2TestCode,it can generate api test case and test data </p>
</div>
"""

with gr.Blocks() as demo:
    with gr.Row():
        gr.HTML(html_title)
    with gr.Row():
        query_str = gr.Textbox(label="query", interactive=True,value="完成pet接口put方法的测试脚本的开发，接口测试脚本的base url是https://petstore3.swagger.io/api/v3")
    with gr.Row():
        with gr.Column(scale=8):
            gen_test_code = gr.Code(label="Generated test code", language="python",
                                        lines=40, interactive=True)
            final_test_code = gr.Code(label="Final test code", language="python",
                                        lines=40, interactive=True)
            code_display=gr.Code(label="test case debug informaiton",lines=20,interactive=False)
        with gr.Column(scale=2):
            json_infor = gr.File()
            upload_button = gr.UploadButton("Click to Upload a json File", file_types=["json"], file_count="single")
            db_infor = gr.Textbox(label="db information", lines=1, interactive=True,value="sqlite:///database/petstore.db")
            tables = gr.Textbox(label="tables", lines=1, interactive=True,value='["pets","category","order","user"]')
            generate_btn = gr.Button(value="Generate testcase")
            param_list = gr.Code(label="param_list",language="python",lines=5,interactive=True)
            request_body = gr.Code(label="request_body",language="python",lines=5,interactive=True)
            request_body_schema = gr.Code(label="request_body_schema",language="python",lines=5,interactive=True)
            gen_test_data=gr.Button(value="Re-generate test data")
            test_data = gr.Code(label="test_data",language="python",lines=5,interactive=True)
            runtest_btn = gr.Button(value="run testcase")
            report_file = gr.File(label="test report")
            testcase_file = gr.File(label="test case")

        
    upload_button.upload(upload_file, upload_button, json_infor)
    generate_btn.click(fn=generate_testcase,inputs=[json_infor,query_str],outputs=gen_test_code).then(
        fn=splite_requestbody,inputs=gen_test_code,outputs=[param_list,request_body]).then(
        fn=gen_requestboduy_shcema,inputs=request_body,outputs=request_body_schema).then(
        fn=gen_testdata,inputs=[db_infor,tables,request_body_schema],outputs=test_data).then(
        fn=get_final_test_code,inputs=[gen_test_code,request_body,param_list,test_data],outputs=final_test_code
        )
    gen_test_data.click(fn=gen_testdata,inputs=[db_infor,tables,request_body_schema],outputs=test_data).then(
        fn=get_final_test_code,inputs=[gen_test_code,request_body,param_list,test_data],outputs=final_test_code
        )
    runtest_btn.click(fn=run_test,inputs=final_test_code,outputs=[code_display,report_file,testcase_file])  
    
demo.launch()

