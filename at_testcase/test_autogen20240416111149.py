#python
import requests
import pytest

# Base URL for the API
base_url = "https://petstore3.swagger.io/api/v3"

# Test data for the DELETE request on /store/order/{orderId}
# Here, we'll test with both a valid and an invalid order ID
delete_request_body_list = [
  {
    "name": "张三",
    "age": 30,
    "email": "zhangsan@example.com"
  },
  {
    "name": "李四",
    "age": 24,
    "email": "lisi@example.com"
  },
  {
    "name": "王五",
    "age": 28,
    "email": "wangwu@example.com"
  },
  {
    "name": "赵六",
    "age": 22,
    "email": "zhaoliu@example.com"
  },
  {
    "name": "孙七",
    "age": 26,
    "email": "sunqi@example.com"
  }
]
param_list = []
param_list_code='''$request_body_code$'''
for aline in request_body_list:
   param_list.append(param_list_code.replace('$request_body_code$',str(aline)))
'''param_list = [
    {
        "url": f"{base_url}/store/order/123",  # Assuming 123 is an existing order ID for testing
        "expected_status_code": 200
    },
    {
        "url": f"{base_url}/store/order/999",  # Assuming 999 is an invalid order ID for testing
        "expected_status_code": 404
    }
]'''

# Pytest function to test the DELETE method
@pytest.mark.parametrize("params", delete_param_list)
def test_delete_order(params):
    # Send the DELETE request
    response = requests.delete(params['url'])
    
    # Assert the response code
    assert response.status_code == params['expected_status_code'], (
        f"Response code was {response.status_code}, expected {params['expected_status_code']}."
    )

# Run the tests
if __name__ == "__main__":
    pytest.main()

if __name__ == '__main__':

    args = ['--report=report.html',
        '--title=测试报告',
        '--tester=测试员',
        '--desc=报告描述信息',
        '--template=1']
    pytest.main(args)