"""
Basic evaluation module for assessing AI response quality.

This is a simplified approach to demonstrate how developers can
detect low-quality or unreliable outputs in AI systems.
"""

def evaluate_response(response):
"""
Evaluate AI response quality based on simple heuristics.
Returns a dictionary with evaluation results.
"""

```
result = {
    "is_valid": True,
    "issues": [],
}

if not response or not response.strip():
    result["is_valid"] = False
    result["issues"].append("Empty response")

# Detect fallback or uncertain responses
fallback_phrases = [
    "i don't know",
    "cannot help with that",
    "not sure",
    "no information available",
]

if any(phrase in response.lower() for phrase in fallback_phrases):
    result["issues"].append("Uncertain or fallback response")

# Detect overly short responses
if len(response.split()) < 5:
    result["issues"].append("Response too short")

# Detect overly long responses (basic heuristic)
if len(response.split()) > 200:
    result["issues"].append("Response too long")

return result
```

def print_evaluation(response):
"""
Print evaluation results in a readable format.
"""

```
evaluation = evaluate_response(response)

print("\n🔍 Evaluation Result")

if evaluation["is_valid"] and not evaluation["issues"]:
    print("✅ Response looks good")
else:
    print("⚠️ Issues detected:")
    for issue in evaluation["issues"]:
        print(f"- {issue}")
```

if **name** == "**main**":
# Example usage
sample_response = "I don't know the answer to that."

```
print("Response:")
print(sample_response)

print_evaluation(sample_response)
```

