from k8s_parser import yaml_to_json
import json

yaml_content = """
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.14.2
    ports:
    - containerPort: 80
"""

try:
    json_output = yaml_to_json(yaml_content)
    parsed_json = json.loads(json_output)
    print(json.dumps(parsed_json, indent=2))
except ValueError as e:
    print(f"Error: {e}")