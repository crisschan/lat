#python
import requests
import pytest

# Base URL for the API
base_url = "https://petstore3.swagger.io/api/v3"

# Test data for the pet (request_body_list = [
  {
    "id": 1,
    "name": "小花",
    "status": "available"
  },
  {
    "id": 2,
    "name": "小黑",
    "status": "pending"
  },
  {
    "id": 3,
    "name": "小白",
    "status": "sold"
  },
  {
    "id": 4,
    "name": "小蓝",
    "status": "available"
  },
  {
    "id": 5,
    "name": "小绿",
    "status": "pending"
  }
]
param_list = []
param_list_code='''param_list=[{"url":f"{base_url}/pet","data":$request_body_code$}]'''
for aline in request_body_list:
   param_list.append(param_list_code.replace('$request_body_code$',str(aline)))
'''param_list with a single entry)
param_list = [
    {
        "url": f"{base_url}/pet",
        "data": {
            "id": 123,
            "name": "TestPet",
            "status": "available"
        }
    }
]'''

# Test function for the PUT method
@pytest.mark.parametrize("params", param_list)
def test_put_pet(params):
    url = params["url"]
    data = params["data"]
    
    # Make a PUT request with the given data
    response = requests.put(url, json=data)
    
    # Assert the response code (assuming it should be 200 for success)
    assert response.status_code == 200, f"Response code should be 200, but got {response.status_code}"
    
    # Assert the length of the response JSON (if we expect a specific length)
    # For example, if we expect the response to have 3 fields
    assert len(response.json()) == 3, "Response JSON length should be 3"

# Run the tests
pytest.main()

if __name__ == '__main__':

    args = ['--report=report.html',
        '--title=测试报告',
        '--tester=测试员',
        '--desc=报告描述信息',
        '--template=1']
    pytest.main(args)