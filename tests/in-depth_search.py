import tavily
import json

# in-depth search

# Initialize client
tavily = tavily.Client(api_key="123456")

# Define query
q = "how does the law protect judicial impartiality against individual judges' biases"

# Run API Call
response = tavily.in_depth_search(q, num_results=3, include_raw_content=False, include_answer=True)

# Print Results
print(json.dumps(response, indent=4))

