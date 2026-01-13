import requests
import json

# Test the GraphQL API
url = 'http://localhost:8000/graphql'

# Test container start mutation
mutation = '''
mutation {
  startContainer(id: "1") {
    id
    name
    status
  }
}
'''

print("Testing container start mutation...")
try:
    response = requests.post(url, json={'query': mutation}, timeout=10)
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print('GraphQL Errors:')
            for error in data['errors']:
                print(f'  {error}')
        else:
            print('Success! Container start mutation worked.')
            container = data.get('data', {}).get('startContainer')
            if container:
                print(f'Container: {container["name"]} - Status: {container["status"]}')
    else:
        print(f'HTTP Error: {response.text}')
except Exception as e:
    print(f'Error: {e}')
