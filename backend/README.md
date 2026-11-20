# Dubai BizNavigator - Backend

Clean Architecture FastAPI backend for Dubai business setup orchestration.

## Layers

- `app/domain`: Pure Python domain entities, value objects, domain exceptions, and port interfaces. Strictly zero dependencies on frameworks or libraries (no FastAPI, no LangChain/LangGraph).
- `app/application`: Application services, use cases, DTOs, and agent workflow coordination.
- `app/infrastructure`: Concrete adapters for persistence (PostgreSQL), external APIs (Tavily search, UAE Banking APIs), agent runtimes (LangGraph/DeepAgents), and observability (Langfuse).
- `app/interfaces`: FastAPI HTTP routes, SSE streaming endpoints, A2UI message serializers, and dependency injection container.
