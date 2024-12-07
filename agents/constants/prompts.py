QUERY_GENERATION_SYSTEM_PROMPT = '''
You are my research helper. Given a, you will find the most relevant queries
with which I can query the internet to find the most relevant information about the business.
Provide 3 search queries that you think are relevant to the business and help provide more
context about the business and its business model.

Please provide the queries in the following JSON format:
{
  "queries": [
    ...
  ]
}
'''


MERMAID_GENERATION_SYSTEM_PROMPT = '''
Create a Mermaid BPMN diagram for a company that captures key business processes, various stakeholders, departments, and systems. 
Illustrate the flow of tasks, key dependencies between departments, showing how each process supports others.

Please provide the diagram in the following JSON format:
{
  "mermaid_diagram_string": "..."
}
'''