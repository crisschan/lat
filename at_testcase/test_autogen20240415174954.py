#python
import requests
import pytest

# Base URL for the petstore API
BASE_URL = "https://petstore3.swagger.io/api/v3"

# The single set of parameters for the test
request_body_list = [
  {
    "id": 1,
    "name": "Max",
    "status": "available"
  },
  {
    "id": 2,
    "name": "Fido",
    "status": "pending"
  },
  {
    "id": 3,
    "name": "Whiskers",
    "status": "sold"
  },
  {
    "id": 4,
    "name": "Lucy",
    "status": "available"
  },
  {
    "id": 5,
    "name": "Rocky",
    "status": "sold"
  }
]
param_list = []
param_list_code='''param_list=[{"url_extension":"/pet","headers":{"Content-Type":"application/json"},"json":$request_body_code$,"expected_status_code":200}]'''
for aline in request_body_list:
   param_list.append(param_list_code.replace('$request_body_code$',str(aline)))
'''param_list = [
    {
        "url_extension": "/pet",  # The specific endpoint after base URL
        "headers": {"Content-Type": "application/json"},
        "json": {"id": 123, "name": "TestPet", "status": "available"},  # The JSON payload for the PUT request
        "expected_status_code": 200  # The expected HTTP status code
    }
]'''

# Pytest test function
@pytest.mark.parametrize("params", param_list)
def test_put_pet(params):
    # Construct the full URL
    url = f"{BASE_URL}{params['url_extension']}"
    
    # Send the PUT request
    response = requests.put(url, headers=params['headers'], json=params['json'])
    
    # Assert the response code
    assert response.status_code == params['expected_status_code'], f"Actual status code: {response.status_code}"
    
    # Assert the response JSON's length
    response_json = response.json()
    assert len(response_json) > 0, "Response JSON is empty"
    
    # Optionally, you can assert for specific values in the response JSON based on the API's response schema
    # assert response_json['id'] == params['json']['id'], "ID in response does not match the sent ID"

# You can run this test using pytest command: pytest test_script.py

if __name__ == '__main__':

    args = ['--report=report.html',
        '--title=测试报告',
        '--tester=测试员',
        '--desc=报告描述信息',
        '--template=1']
    pytest.main(args)