#python
import requests
import pytest

# Base URL for the petstore API
BASE_URL = "https://petstore3.swagger.io/api/v3"

# The single parameter list that includes the necessary parameters for the PUT request
request_body_list = [
  {
    "id": 1,
    "name": "Max",
    "status": "sold"
  },
  {
    "id": 2,
    "name": "Lucy",
    "status": "sold"
  },
  {
    "id": 3,
    "name": "Charlie",
    "status": "sold"
  },
  {
    "id": 4,
    "name": "Daisy",
    "status": "sold"
  },
  {
    "id": 5,
    "name": " Cooper",
    "status": "sold"
  }
]
param_list = []
param_list_code='''param_list=[{"url_suffix":"/pet","headers":{"Content-Type":"application/json"},"json":$request_body_code$,"expected_status_code":200}]'''
for aline in request_body_list:
   param_list.append(param_list_code.replace('$request_body_code$',str(aline)))
'''param_list = [
    {
        "url_suffix": "/pet",  # The URL suffix for the pet endpoint
        "headers": {"Content-Type": "application/json"},
        "json": {"id": 123, "name": "Mittens", "status": "sold"},  # Example payload
        "expected_status_code": 200  # The expected HTTP status code
    }
]'''

# Pytest test function
@pytest.mark.parametrize("params", param_list)
def test_put_pet(params):
    # Making a PUT request with the given parameters
    response = requests.put(BASE_URL + params["url_suffix"], headers=params["headers"], json=params["json"])
    
    # Asserting the response code
    assert response.status_code == params["expected_status_code"], f"Expected status code {params['expected_status_code']} but got {response.status_code}"
    
    # Asserting the length of the response json
    response_json_length = len(response.json())
    assert response_json_length > 0, f"Response JSON length is zero. Response: {response.text}"

# You can run the tests using the following command:
# pytest -v test_script.py

if __name__ == '__main__':

    args = ['--report=report.html',
        '--title=测试报告',
        '--tester=测试员',
        '--desc=报告描述信息',
        '--template=1']
    pytest.main(args)