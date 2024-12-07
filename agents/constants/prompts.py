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
Create a colourful and intuitive, Mermaid BPMN diagram for a company that captures key business processes, various stakeholders, departments, and systems. 
Illustrate the flow of tasks, key dependencies between departments, showing how each process supports others.

Please provide the diagram in the following JSON format:
{
  "mermaid_diagram_string": "..."
}
'''


ANALYZE_MERMAID_GENERATION_SYSTEM_PROMPT = '''
This a BPMN of a company. In which thing can I use blockchain technologies and use tokenisation and not to make a footprint in the web3 world.
Give a list of ways you can use blockchain technologies to improve the business processes and make it more efficient. Give references to the mermaid diagram.
Provide the list in the following JSON format, only use tokenisation, nfts, defi and security/traceability, Give examples of companies that have used these technologies:
{
  "ways": [
    {
      "usecase": "...",
      "description": "...",
      "technology_name": "...",
      "department_it_will_improve": "",
      "companies": [
        "...
      ]
    }
    ...
  ]
}
'''


ALTER_MERMAID_GENERATION_SYSTEM_PROMPT = '''
You are an amazing diagram drawer. I will pass you mermaid string, I want you to alter the mermaid diagram.
Based on the improvement add it to the mermaid diagram. Send back to me in the same JSON format given below in the output.
Input Format: {
  "improvement": {
      "usecase": "...",
      "description": "...",
      "technology_name": "...",
      "department_it_will_improve": "",
      "companies": [
        "...
      ]
    }
}

Output_Format: {
  "mermaid_diagram_string": "..."
}
'''