# RAPID: Real AI-Powered Insights on Demand

## Problem Statement

Today, we lack a centralized repository where we consistently create and submit customer stories. This is needed to inspire colleagues, provide tangible stories to leadership about the work we are doing, and share knowledge across pods about ideas that can be taken to other customers.

Creating a large corpus of customer stories is time-consuming, and much of the data needed for creating the stories is available in other systems. Starting from scratch requires a certain level of redundancy in resubmitting information. Additionally, any customer stories being produced today are not centrally available and are being created for ad-hoc scenarios within specific teams.

## Solution: RAPID

RAPID will revolutionize our storytelling process by creating a compelling, easy-to-use, and centralized destination for our wins, all powered by AI.

## Key Features

- **Centralized Repository**: A beautiful, central location for all AI customer wins.
- **Organized Stories**: Stories are organized by industry, business function, and scenario.
- **AI-Powered Insights**: Learn from a large body of customer stories. Our AI finds patterns and similarities across industry use cases.
- **End-to-End Automation**: An end-to-end AI-powered automation with a modern application interface for submitting new stories.

## Process Flow

1. Initial Question posed by LLM is to gather ADO ID.
2. LLM uses function calling to grab ADO data as JSON as well as customer info via Bing search.
3. Generates initial draft.
4. Additional LLM instance evaluates initial draft for completeness.
5. LLM asks additional follow up questions it needs to build a stronger narrative.
6. User approves draft.
7. If edits are needed, the user asks for edits via the chat interface.
8. Repeat until approved.
9. LLM generates the story as markdown files (converted to HTML/ASPX for SharePoint).
10. Users can search for content on the web app.

## Getting Started

To use this project, follow these steps:

1. Clone the repository: `git clone <repository-url>`
   - Optional: 
     - Navigate to the parent of the project directory: `cd ..\<project-directory>`
     - Open in VS Code: `code <project-folder-name>`
2. Copy `.env.sample` to a new file called `.env` and configure the settings: `copy .env.sample .env`
    
    These variables are required:
    - `AZURE_OPENAI_RESOURCE`
    - `AZURE_OPENAI_ENDPOINT`
    - `AZURE_OPENAI_API_KEY`
    - `AZURE_OPENAI_API_VERSION`
    - `AZURE_OPENAI_DEPLOYMENT_NAME`
    - `AZURE_OPENAI_MODEL`

    These variables are optional:
    - `AZURE_OPENAI_TEMPERATURE`
    - `AZURE_OPENAI_TOP_P`
    - `AZURE_OPENAI_MAX_TOKENS`
    - `AZURE_OPENAI_STOP_SEQUENCE`
    - `AZURE_OPENAI_SYSTEM_MESSAGE`

    See the [documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#example-response-2) for more information on these parameters.

3. Start the app with `start.cmd`. This will build the frontend, install backend dependencies, and then start the app. Or, just run the backend in debug mode using the VSCode debug configuration in `.vscode/launch.json`.

4. You can see the local running app at http://127.0.0.1:50505.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these guidelines:

1. Fork the repository
2. Create a new branch: `git checkout -b <branch-name>`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin <branch-name>`
5. Submit a pull request

## Acknowledgements

This project was forked from [Microsoft's sample-app-aoai-chatGPT](https://github.com/microsoft/sample-app-aoai-chatGPT.git). (Under [MIT License](LICENSE) agreement)

## License

This project is licensed under the [MIT License](LICENSE).
