#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   exec_text.py
@Time    :   2024/04/10 01:39:28
@Author  :   CrissChan 
@Version :   1.0
@Site    :   https://blog.csdn.net/crisschan
@Desc    :   按照生成python的代码，处理代码文本
'''
import json

class ExecText(object):
    def __init__(self, text) -> None:
        self.text = text
        self.start_index = -1
        self.end_index = -1
        pass

    def set_values_to_none(self,data):

        if isinstance(data, dict):
            # 如果是字典，遍历其键值对
            for key, value in data.items():
                # 递归调用函数处理值
                if isinstance(value, dict) or isinstance(value, list):
                    self.set_values_to_none(value)
                else:
                    # 将值设置为None
                    if key.find("method")!=-1 or key.find("endpoint")!=1 or key.find("expected_status")!=1:
                        continue
                    else:
                        data[key] = None
            # 将所有值设置为None
            # data.clear()
        elif isinstance(data, list):
            # 如果是列表，遍历其元素
            for item in data:
                # 递归调用函数处理元素

                if isinstance(item, dict) or isinstance(item, list):
                    self.set_values_to_none(item)
                else:
                    data.pop()
            data.pop()
    def replace_all_curlybracket(self,data):
        while data.find('f"{')!=-1:
            data = self.replace1curlybracket(data)
        return data
    def replace1curlybracket(self,data):
        left_index =data.find('f"{')
        right_index=data.find('}/"')
        if  left_index!=-1 and right_index!=-1:
            data = data.repalace('f"{','f"\\{').repalace('}/"','\\}/"')
        return data
    def mulitline2oneline(self,data:str)->str:
        '''
        @des  :删除字符串中的换行和空格
        @params  :需要处理的字符串
       
        '''
        return data.replace("\r","").replace("\n","").replace(" ","")
    def del_all_comments(self,data:str)->str:
        '''
        @des  :删除代码段中全部的注释
        @params  : data 代码段字符串
        '''
        
        while  data.find("#")!=-1:
            data = self.del1comment(data,"#","\n")
        # self.replace_all_curlybracket(data)
        return data
    def del1comment(self,data:str,start:str,end:str)->str:
        '''
        @des  :在data中删除第一个以start开始end结束的子串
        @params  : data 需要处理的字符串
                   start 删除子串开始标记
                   end 删除子串的结束标记
        '''
        
        
        start_index = data.find(start)
        end_index = start_index+data[start_index:].find(end)
        if start_index!=-1 and end_index!=-1:
            return data[:start_index]+data[end_index+1:]
        else:
            return data
    def find_param_list(self)->str:
        '''
        @des  :找到param_list数据驱动部分的代码（废弃了，但是其他部分还需要用到这里处理的数据，就保留了函数）
               函数目前仅处理找到start_index和end_index

        @params  :
        '''
        
        
        # 找到第一个标记的索引和第二个标记的索引
        
        self.start_index = self.text.find('param_list')
        if self.start_index != -1:
            self.end_index = self.start_index + \
                self.text[self.start_index:].find(']')
        else:
            self.start_index =-1
            self.end_index=-1

        # # 如果两个标记都存在
        # if self.start_index != -1 and self.end_index != -1:
        #     # 并且第二个标记在第一个标记之后

        #     if self.end_index > self.start_index:
        #         # 提取两个标记之间的内容
        #         between_markers = self.text[self.start_index:self.end_index+1]
        #         # between_markers=self.del_all_comments(between_markers)
        #         # param_last=[]
        #         # for aline in  json.loads(between_markers):
        #         #     self.set_values_to_none(aline)
        #         #     param_last.append(aline)
        #         # param_last=json.dumps(self.set_values_to_none(json.loads(between_markers)))
        #         return between_markers
        #     else:
        #         raise Exception(
        #             "Gen python code has some error with the list end mark ].")

    def replace_gen_code(self, request_body_code:str,param_list_code:str,new_param:str)->str:
        '''
        @des  :最后一步需要的函数，将生成的数据和生成的测试代码组合到一个脚本中。
        @params  :request_body_code 数据驱动部分提供给请求的request body代码，这个第一次生成的代码部分
                  param_list_code 数据驱动的参数列表，这也是第一次生成的代码部分
                  new_param 生成的测试数据
        @ return :最终生成的脚本，如果没有需要替换的，直接返回生成code
        '''
        
        
        request_body_code=self.del_all_comments(request_body_code)
        param_list_code=self.del_all_comments(param_list_code)
        new_param=self.del_all_comments(new_param)
     
        
        request_body_code_2 = self.mulitline2oneline(request_body_code)
        param_list_code_2=self.mulitline2oneline(param_list_code)
        param_list_temp = param_list_code_2.replace(request_body_code_2,"$request_body_code$")
        self.find_param_list()
        # 如果两个标记都存在
        param_list_gen=(
                    "param_list = []\n"
                    "param_list_code='''"+param_list_temp+"'''\n"
                    "for aline in request_body_list:\n"
                    "   param_list.append(param_list_code.replace('$request_body_code$',str(aline)))\n"
        )
        if self.start_index != -1 and self.end_index != -1:
            self.text = self.text[:self.end_index+1] + \
                "'''"+self.text[self.end_index+1:]
            self.text = self.text[:self.start_index] + \
                "request_body_list = "+new_param+"\n"+f"{param_list_gen}"+"'''"+self.text[self.start_index:]
        return self.text
        # else:
        #     raise Exception("please run find_param_list() first")


# if __name__ == '__main__':
#    newparam =''' [
#   {
#     "id": 1,
#     "name": "宠物1号",
#     "status": "available"
#   },
#   {
#     "id": 2,
#     "name": "宠物2号",
#     "status": "sold"
#   },
#   {
#     "id": 3,
#     "name": "宠物3号",
#     "status": "sold"
#   },
#   {
#     "id": 4,
#     "name": "宠物4号",
#     "status": "available"
#   },
#   {
#     "id": 5,
#     "name": "宠物5号",
#     "status": "sold"
#   },
#   {
#     "id": 6,
#     "name": "宠物6号",
#     "status": "sold"
#   },
#   {
#     "id": 7,
#     "name": "宠物7号",
#     "status": "available"
#   },
#   {
#     "id": 8,
#     "name": "宠物8号",
#     "status": "sold"
#   }
# ]'''

# param_list_code='''[
#     {"path": "/pet", "data": {"id": 1, "name": "Dog", "status": "available"}, "expected_length": 1},
#     {"path": "/pet", "data": {"id": 2, "name": "Cat", "status": "sold"}, "expected_length": 1}
# ]'''

# request_body_code='''{
#     "id": 1,
#     "name": "Dog",
#     "status": "available"
# },
# {
#     "id": 2,
#     "name": "Cat",
#     "status": "sold"
# }'''

# text='''import requests
# import pytest

# # Base URL for the API
# base_url = "https://petstore3.swagger.io/api/v3"

# # Test data parameters for the POST request
# param_list = [
#     {"param1": "value1", "param2": "value2"},  # Replace with actual parameters and values required for your API
#     # Add more parameter sets as needed
# ]

# # Test function using pytest.mark.parametrize to test different parameter sets
# @pytest.mark.parametrize("params", param_list)
# def test_pet_post_method(params):
#     # Endpoint for the pet interface
#     endpoint = "/pet"
#     # Full URL
#     url = base_url + endpoint
#     # Payload for the POST request (assuming params is a dictionary that needs to be sent as JSON)
#     payload = params
    
#     # Sending the POST request
#     response = requests.post(url, json=payload)
    
#     # Asserting the response code
#     assert response.status_code == 201, f"Response code is not 201. Actual: {response.status_code}"
    
#     # Asserting the length of the response JSON
#     response_length = len(response.json())
#     assert response_length > 0, f"Response JSON is empty or not as expected. Length: {response_length}"'''

# et = ExecText(text)
# # print(et.replace_gen_code(request_body_code=request_body_code,param_list_code=param_list_code,new_param=newparam))