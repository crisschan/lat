#python
import requests
import pytest

# Base URL for the API
base_url = "https://petstore3.swagger.io/api/v3"

# Test suite
@pytest.mark.parametrize("params", [{}])  # Empty params as the endpoint does not require parameters
def test_get_inventory(params):
    # URL for the specific endpoint
    url = f"{base_url}/store/inventory"
    
    # Make the GET request
    response = requests.get(url)
    
    # Assert the response code (expecting 200 OK)
    assert response.status_code == 200
    
    # Additional assertions can be added here based on the expected response data
    # For example, if you expect an non-empty inventory, you can assert:
    assert isinstance(response.json(), list)
    # If you have a specific length expected, you can assert that as well:
    # expected_length = ...  # Set the expected length
    # assert len(response.json()) == expected_length

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