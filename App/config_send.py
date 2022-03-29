import requests

response = requests.post("http://localhost:5000/config/", data="configuration.yaml")
print(response.status_code)

