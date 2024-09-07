# Guide for Running Tests and Modifying Components

## Running Tests

1. **Setup**:
   - Ensure you have pytest and pytest-asyncio installed:
     ```
     pip install pytest pytest-asyncio
     ```
   - Make sure you're in the root directory of the project.

2. **Running All Tests**:
   ```
   pytest tests/
   ```

3. **Running Specific Test Files**:
   ```
   pytest tests/test_main.py
   pytest tests/test_quantum_task_optimizer.py
   ```

4. **Running Specific Test Functions**:
   ```
   pytest tests/test_main.py::test_websocket_connection
   ```

5. **Running Tests with Detailed Output**:
   ```
   pytest -v tests/
   ```

6. **Running Tests and Stopping on First Failure**:
   ```
   pytest -x tests/
   ```

## Modifying Components

1. **Identify the Component**:
   - Locate the component you want to modify in the `app/` directory.

2. **Make Changes**:
   - Open the file and make your desired changes.
   - Ensure you maintain the existing function signatures to avoid breaking dependencies.

3. **Update Tests**:
   - Find the corresponding test file in the `tests/` directory.
   - Update existing tests or add new ones to cover your changes.

4. **Run Relevant Tests**:
   - Run the tests for the modified component:
     ```
     pytest tests/test_<component_name>.py
     ```

5. **Update Documentation**:
   - If your changes affect the API or functionality, update the relevant documentation.

6. **Integration Testing**:
   - Run the full test suite to ensure your changes don't break other components:
     ```
     pytest tests/
     ```

7. **Commit Changes**:
   - If all tests pass, commit your changes with a descriptive commit message.

## Example: Modifying the QuantumTaskOptimizer

1. Open `app/quantum/quantum_task_optimizer.py`
2. Make your changes to the `QuantumTaskOptimizer` class
3. Open `tests/test_quantum_task_optimizer.py`
4. Update existing tests or add new ones
5. Run the specific tests:
   ```
   pytest tests/test_quantum_task_optimizer.py
   ```
6. If the tests pass, run the full test suite:
   ```
   pytest tests/
   ```
7. Update any relevant documentation
8. Commit your changes

## Best Practices

- Always write tests for new functionality
- Ensure all tests pass before committing changes
- Use type hints and docstrings for better code readability
- Follow the existing code style and conventions
- Consider the impact of your changes on other components
- Use meaningful variable and function names
- Comment complex logic for better understanding

Remember, our AGI system is highly interconnected. A change in one component might affect others, so thorough testing is crucial.