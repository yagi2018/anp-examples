# anp-examples
anp-examples

Develop an ANP example application

It consists of two parts:

1. **ANP Agent**
The entry point of the agent is an agent description document. Through this document, connections to internal agent data can be established. The agent description document, combined with internal data such as additional JSON files, images, and interface files, constitutes the public information of the agent. It is recommended to use a hotel agent as an example. Construct the agent's data, including a hotel description, services provided by the hotel, customer service details, and booking interfaces. Use FastAPI to return the relevant documents based on requests. I can provide sample documents for the hotel agent.

2. **ANP Client**
Develop a client that accesses the ANP agent. The client will feature a page that accepts a URL pointing to an agent description document. With this document URL, the client can access all information from the agent, including services, products, and API endpoints like hotel booking interfaces. The page should clearly display which URLs the client accessed and the content retrieved, allowing users to visually follow the interaction process.


