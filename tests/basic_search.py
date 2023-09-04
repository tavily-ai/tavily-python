import tavily
import json

# Basic search

# Initialize client
tavily = tavily.Client(api_key="123456")

# Define query
q = "how does the law protect judicial impartiality against individual judges' biases"

# Run API Call
response = tavily.basic_search(q, num_results=10, include_raw_content=False)

# Print Results
print(json.dumps(response, indent=4))

