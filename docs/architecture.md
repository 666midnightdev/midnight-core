# Midnight Core: Architecture Reference Document

Midnight Core is a local-first DevSecOps agent and AI operating platform structured around Clean Architecture principles. It enforces strict separation of concerns, decouples reasoning from action, and provides an audited sandboxed execution environment.

```
                  +-----------------------------------+
                  |        CLI / Web Dashboard        |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |         Core Orchestrator         |
                  +-------+---------+---------+-------+
                          |         |         |
            +-------------+         |         +-------------+
            v                       v                       v
      +-----+------+         +------+-----+          +------+-----+
      |   Planner  |         | Memory/RAG |          |  Executor  |
      +------------+         +------------+          +---+----+---+
                                                         |    |
                                             +-----------+    +-----------+
                                             v                            v
                                    +--------+--------+          +--------+--------+
                                    | Local OS Runner |          | WSL Kali Runner |
                                    +-----------------+          +-----------------+
```

## Modular Separation of Responsibilities

1. **core**: Coordinates the main operational lifecycle. It feeds user requests to the Planner, iterates over generated steps, invokes the permission-audited execution layer, logs results in Memory, and routes outputs to the Report Generator.
2. **planner**: Responsible for goal decomposition. It queries Ollama using schemas of registered tools to create a logical plan.
3. **executor**: Executes commands locally or inside a WSL distribution (Kali Linux). It handles command validation, user approval prompts, timeouts, and process cancellation.
4. **memory**: Implements conversation logging, task tracking, tool execution audits, and vector storage using a local SQLite backend.
5. **rag**: Extracts, chunks, embeds, and indexes source code (.py, .js, .ts, .php), configuration files (.json, .yaml), and documents (.pdf, .docx).
6. **mcp**: A stdio-based implementation of the Model Context Protocol, allowing Midnight Core tools to be exposed directly to cursor, copilot, or other compliant AI IDEs.
7. **providers**: Handles communication with the local Ollama endpoint (Chat & Embeddings).
8. **tools**: Contains built-in utilities registered via decorators for filesystem operations, network scans, and system inspection.
9. **reports**: Compiles vulnerabilities into Markdown, JSON, and rich HTML assessment files.
