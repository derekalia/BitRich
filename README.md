# BitRich

BitRich is a sophisticated AI-powered automation framework inspired by Claude's UseComputer. The project is designed to automate screen interactions by taking screenshots, understanding the current state of the screen, and performing tasks based on user goals using a combination of agents. It utilizes OmniParser for parsing screen content and LLaMA for generating subgoals and Python code to execute actions.

## Overview

BitRich consists of three primary agents:

1. **Mother Agent**: Manages user-inputted goals, generates subgoals, and coordinates the entire process until the goal is met.
2. **Action Agent**: Processes screenshots, identifies elements using OmniParser, and generates Python code to perform the subgoal.
3. **DoubleCheck Agent**: Verifies if the subgoal was successfully completed by comparing the current screen state with the expected outcome.

## Project Structure

```
BitRich/
├── mother_agent.py          # Main file for managing user goals and subgoals
├── do_agent.py              # Action Agent that processes subgoals and executes them
├── doubleCheckAgent.py      # DoubleCheck Agent for verification of subgoal completion
├── requirements.txt         # Python dependencies
├── .env                     # Environment file for API keys
├── README.md                # Project documentation
└── logs/                    # Directory for log files
```

## Key Features

- **Goal Management**: The Mother Agent breaks down user goals into actionable subgoals and coordinates their execution.
- **Automated Screen Interaction**: The Action Agent generates and runs Python code to perform tasks on the screen.
- **State Verification**: The DoubleCheck Agent ensures each subgoal is completed by analyzing the screen state.

## How It Works

1. **User Input**: The Mother Agent receives an overall user goal.
2. **Screen Analysis**: The current state of the screen is captured and analyzed using OmniParser and LLaMA.
3. **Subgoal Creation**: The Mother Agent generates subgoals and passes them to the Action Agent.
4. **Action Execution**: The Action Agent generates and executes Python code to perform the subgoal.
5. **Verification**: The DoubleCheck Agent verifies if the subgoal was completed. If not, the Mother Agent refines and retries.
6. **Iteration**: The process repeats until the overall goal is completed.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/BitRich.git
    cd BitRich
    ```

2. **Set up a virtual environment (recommended)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your `.env` file**:
    Create a `.env` file in the root directory with your API key:
    ```
    OPENROUTERAPIKEY=your_openrouter_api_key_here
    ```

## Usage

1. **Run the main program**:
    ```bash
    python mother_agent.py
    ```

2. **Enter your goal** when prompted. The system will iterate through the agents to achieve it.

## Agents Description

### Mother Agent
- Responsible for managing the overall user goal.
- Generates subgoals and coordinates their execution.
- Logs progress and refines goals if necessary.

### Action Agent
- Processes subgoals by generating Python code to interact with the screen.
- Uses OmniParser to identify elements and LLaMA for code generation.

### DoubleCheck Agent
- Verifies if the subgoal has been completed by comparing the current screen state with the expected result.
- Returns `true` if successful and `false` otherwise.

## Logging

Logs for the agents' actions are stored in separate log files to help with debugging and tracking the automation process.

## Contributing

Contributions are welcome! Please create an issue or submit a pull request for major changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For questions or suggestions, feel free to reach out or submit an issue on GitHub.

