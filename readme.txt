Create a comprehensive Python project for an advanced LLM-based agent system that can dynamically solve any software development task. The system should be highly modular, extensible, and capable of creating and managing multiple LLM agents that work together in a virtual environment. The project should include the following major components and features:

1. Main Application:
   - Implement a FastAPI-based main application that serves as the entry point.
   - Include API endpoints for interacting with the system, starting projects, and checking project status.
   - Implement WebSocket support for real-time updates.

2. Agent System:
   - Create a base Agent class that all specialized agents will inherit from.
   - Implement an AgentFactory for dynamically creating and customizing agents based on task requirements.
   - Develop a multi-agent collaboration system that allows agents to work together on complex tasks.

3. Virtual Environment:
   - Design a VirtualEnvironment class that simulates a development environment.
   - Implement methods for creating, modifying, and deleting virtual files and directories.
   - Include a mechanism for agents to interact with the virtual environment.

4. Physical Workspace:
   - Create a WorkspaceManager class that interfaces with the actual file system.
   - Implement methods for reading, writing, and manipulating files in the physical workspace.
   - Ensure proper synchronization between the virtual environment and physical workspace.

5. Task Management:
   - Develop a TaskManager class for breaking down complex tasks into subtasks.
   - Implement a priority queue system for task scheduling.
   - Create a WorkflowEngine for managing the execution of multi-step tasks.

6. Skill System:
   - Design a modular skill system where each skill is a separate class (e.g., CodingSkill, RefactoringSkill, TestingSkill).
   - Implement a SkillManager for registering, retrieving, and executing skills.
   - Ensure skills can be dynamically loaded and unloaded.

7. Knowledge Management:
   - Implement a KnowledgeGraph class using Neo4j for storing and retrieving information.
   - Create a LearningEngine that allows agents to learn from their experiences and update the knowledge graph.
   - Develop a QueryEngine for complex knowledge retrieval operations.

8. Natural Language Processing:
   - Create an NLParser class for parsing natural language inputs into structured task descriptions.
   - Implement a TaskClassifier for categorizing tasks based on their descriptions.
   - Develop an NLGenerator for producing human-readable outputs and explanations.

9. Code Generation and Analysis:
   - Implement a CodeGenerator class that can produce code based on high-level descriptions.
   - Create a CodeAnalyzer for reviewing and optimizing generated code.
   - Develop a TestGenerator for automatically creating unit tests.

10. Project Management:
    - Design a ProjectManager class for handling multi-file, multi-directory projects.
    - Implement version control integration (e.g., Git) for managing code changes.
    - Create a DocumentationGenerator for automatically generating project documentation.

11. User Interface:
    - Develop a command-line interface for interacting with the system.
    - Implement a web-based dashboard for visualizing system status, agent activities, and project progress.

12. Security and Ethics:
    - Implement a SecurityManager for ensuring safe execution of generated code.
    - Create an EthicsChecker for evaluating the ethical implications of agent actions and generated code.

13. Logging and Monitoring:
    - Develop a comprehensive logging system for tracking agent activities and system events.
    - Implement a PerformanceMonitor for analyzing and optimizing system performance.

14. Error Handling and Recovery:
    - Create a robust error handling system that can recover from failures gracefully.
    - Implement a mechanism for agents to learn from and adapt to errors.

15. Extension and Plugin System:
    - Design a plugin architecture that allows for easy extension of the system's capabilities.
    - Implement a PluginManager for loading, unloading, and managing plugins.

16. Configuration and Environment Management:
    - Create a ConfigManager for handling system-wide and project-specific configurations.
    - Implement an EnvironmentManager for managing different runtime environments (e.g., development, testing, production).

Ensure that the entire system is asynchronous where appropriate, using Python's asyncio library. Implement proper error handling, logging, and documentation throughout the codebase. Use type hints and follow PEP 8 guidelines for code style.

The system should be designed with scalability in mind, capable of handling multiple projects and tasks simultaneously. Implement appropriate design patterns and SOLID principles throughout the architecture.

Provide a detailed README.md file with instructions for setting up and running the system, including any necessary dependencies and environment variables.

Generate the complete code for this project, organizing it into appropriate modules and packages. Include all necessary classes, functions, and methods to create a fully functional system.




data retrieval pipelines and data implementation pipelines that self iterate on itself deciding the next best step to develop a really autonomous agent to complete anything

high information entropy algorithm to not go decoherent and to be able to do anything and gain temporal awareness