import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.core.agent import agent

def test_suggestions():
    df = pd.read_csv('sample_data.csv')
    print("Generating suggestions for sample_data.csv...")
    suggestions = agent.generate_suggestions(df)
    print("\nSuggestions:")
    for s in suggestions:
        print(f"- {s}")
    
    print("\nTesting dashboard generation for 'create a bi dashbord for me'...")
    analysis = agent.analyze_query("create a bi dashbord for me", df)
    print("Analysis Keys:", analysis.keys())
    print("Viz type:", analysis.get('viz'))

if __name__ == "__main__":
    test_suggestions()
