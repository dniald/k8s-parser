# Kubernetes YAML to JSON Parser

- Manual YAML parsing implementation
- Basic validation of Kubernetes resource structure
- Validation of required Kubernetes fields (apiVersion, kind, metadata)
- Output to file or stdout

## Usage

#### Script (k8s_yaml_converter.py)

```bash
# convert a yml file to json and print to stdout
python3 k8s_parser.py deployment.yaml

# convert a yml file to json and save to a file
python3 k8s_parser.py deployment.yaml -o output.json

# convert to yml file from cli
python3 k8s_parser.py $'apiVersion: v1\nkind: Pod\nmetadata:\n  name: test-pod' -o svc.json
```

#### Simplified Script (k8s_parser.py)

```bash
# convert a yml file to json and print to stdout
python3 k8s_parser.py -f deployment.yaml

# convert a yml file to json and save to a file named 'output'
python3 k8s_parser.py -f deployment.yaml -o output.json
```

### Python Library Usage

for direct access to the parsed Python object, use `parse_simple_yaml()`.

```python3
from k8s_parser import yaml_to_json
import json

yaml_content = """
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    app: web
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
```