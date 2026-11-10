# Getnet Multi-Agent Support System

## 1. Objective
Build a multi-agent customer support system using Python, FastAPI, Ollama, and Retrieval-Augmented Generation (RAG).

Development methodology: Spec-Driven Development (SDD).

The system routes customer requests to specialized agents, retrieves information from official Getnet Mexico sources, performs real web searches, queries simulated customer records, and creates simulated escalation tickets.

## 2. Functional Requirements
### FR-001: Router Agent
- Analyze incoming user messages using Qwen3.
- Classify requests as knowledge, support, or both.
- Validate structured routing decisions using Pydantic.
- Route requests to the appropriate specialized agents.
- Support combined requests requiring multiple agents.
- Provide a fallback route when classification fails.
### FR-002: Knowledge Agent
- Retrieve Getnet product information using RAG.
- Ingest publicly accessible documentation from the official Getnet Mexico website.
- Generate local embeddings using nomic-embed-text.
- Store and retrieve document chunks using persistent ChromaDB storage.
- Perform real external web searches for general questions using DDGS.
- Return source URLs alongside generated answers.
- Avoid unsupported claims and treat retrieved content as untrusted evidence.
- Handle unavailable or insufficient information gracefully.
### FR-003: Customer Support Agent
- Retrieve simulated customer information using Python tools.
- Implement get_customer(user_id) and get_transactions(user_id).
- Store mock customer and transaction records in JSON files.
- Scope data retrieval to the supplied user_id.
- Generate responses based on retrieved customer records.
- Return appropriate responses for unknown customers.
Security limitation: The MVP does not implement user authentication or authorization. The supplied user_id determines which simulated records are retrieved and must not be treated as verified identity.
### FR-004: Escalation Agent
- Detect requests requiring human assistance using predefined rules.
- Identify explicit human-support requests and selected sensitive scenarios.
- Create simulated escalation tickets in SQLite.
- Return a simulated ticket reference.
- Return the pending_human_review status.
- Clearly distinguish simulated escalation from actual human notification.
### FR-005: Response Quality and Personality
- Produce clear, professional, and consistent responses.
- Respond in Spanish or English according to the user's language.
- Preserve retrieved facts and relevant source references.
- Avoid fabricating transaction details, deposit dates, fees, or Getnet policies.
- Return a defined status when information cannot be retrieved.

## 3. System Architecture
The application consists of:
- FastAPI: HTTP API and request validation.
- Escalation Agent: Rule-based escalation detection and ticket creation.
- Router Agent: LLM-based request classification.
- Knowledge Agent: RAG retrieval and external web search.
- Support Agent: Simulated customer and transaction retrieval.
- Ollama: Local LLM inference and embedding generation.
- ChromaDB: Persistent vector storage.
- SQLite: Simulated escalation ticket persistence.

Request Processing
1. Receive a request through POST /chat.
2. Validate the request using Pydantic.
3. Evaluate escalation rules.
4. If escalation is required, create a simulated ticket.
5. Otherwise, classify the request using the Router Agent.
6. Execute the Knowledge Agent, Support Agent, or both.
7. Combine results when multiple agents are required.
8. Return a structured JSON response.

## 4. API Contract

POST /chat
Request
{
  "message": "When will my last sale be deposited?",
  "user_id": "cliente001"
}

Response fields
- answer: Generated response.
- agents_used: List of agents involved.
- sources: Source URLs used for retrieval.
- status: Processing result.

Supported status values
- success
- insufficient_information
- pending_human_review
- error

GET /health
Returns the application's basic health status.

## 5. Technical Requirements
- Python 3.12
- FastAPI and Pydantic
- Ollama with qwen3:4b
- nomic-embed-text embeddings
- ChromaDB persistent vector database
- DDGS external web search
- SQLite for simulated escalation tickets
- Docker containerization
- pytest automated testing
- Environment-based configuration

## 6. Data Sources
Official Getnet Mexico documentation
The initial RAG knowledge base includes:
- Getnet payment terminal with printer
- Getnet Portal
Source domain: www.getnet.net/mx/
Simulated customer information
- data/customers.json
- data/transactions.json

## 7. Acceptance Criteria
- Router classifies requests into the supported routes.
- Knowledge Agent retrieves official Getnet Mexico documents.
- General questions can trigger real external web searches.
- Support Agent executes at least two customer-data tools.
- Customer records are filtered by the supplied user_id.
- Combined requests can invoke multiple specialized agents.
- Escalation requests create simulated tickets.
- API returns JSON matching the defined response schema.
- Errors and unavailable sources are handled without fabricating answers.
- Docker execution and automated tests are documented.

## 8. Validation
The MVP has passed 21 automated pytest tests, covering API behavior, routing, simulated customer data, knowledge classification, escalation behavior, and selected error scenarios.

These automated tests do not establish production readiness or guarantee the accuracy of all LLM-generated responses.

## 9. Known Limitations
- No production authentication or authorization.
- No connection to real Getnet customer accounts or transaction systems.
- Escalation tickets do not notify actual human operators.
- The RAG corpus covers a limited selection of official Getnet Mexico pages.
- External web search depends on third-party provider availability.
- LLM responses may still require factual verification.
- Local Ollama inference requires sufficient computing resources.

## 10. Future Improvements
- Implement authentication and authorization.
- Expand official Getnet Mexico knowledge coverage.
- Add retrieval relevance thresholds and citation verification.
- Introduce structured observability and performance metrics.
- Add integration and end-to-end tests.
- Connect escalation workflows to an authorized human-support platform.
- Improve deployment portability and operational monitoring.