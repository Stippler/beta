# Wheather or not

This FastAPI application provides a backend service for managing and analyzing events, tasks, and schedules. It integrates with OpenAI's API for text analysis and uses MongoDB for data persistence. The application supports CRUD operations for tasks, text analysis for extracting event details from text, and proposing new event times based on given inputs.

## Features

- **Task Management:** Create, read, update, and delete tasks or events.
- **Text Analysis:** Analyze text to extract and structure event details using OpenAI's API.
- **Date Proposal:** Suggest new event times based on the analysis of provided details.
- **Weather Check:** Placeholder endpoints for weather-related functionalities (to be implemented).

## Installation

1. Clone the repository to your local machine.
2. Ensure you have Python 3.8+ installed.
3. Install dependencies:

```
pip install -r requirements.txt
```

4. Set up your `.env` file in the root of the project with your OpenAI API key and Mongo DB key:

## Running the Application

Run the application using Uvicorn:

```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This will start the server on `localhost:8000`.

## Endpoints

- **GET /**: Returns a hello message.
- **POST /task/**: Adds a new task.
- **GET /task/**: Lists all tasks.
- **PUT /task/**: Updates a task.
- **PUT /task/{id}**: Deletes a task.
- **POST /text/**: Analyzes text to fill out a predefined event template.
- **POST /text_list/**: Analyzes a list of texts.
- **POST /propose/**: Proposes a new date for an event.
- **POST /weather/**: Placeholder for fetching weather data.
- **POST /ok/**: Placeholder for checking if the weather is suitable for an event.

## Models

- **Task**: Represents an event or task with details like title, date, and activity type.
- **WeatherRequest**: Used for weather-related endpoints (to be implemented).
- **TextRequest**: Contains text for analysis.
- **TextListRequest**: Contains a list of texts for analysis.

## Note

This application is a template and requires further development for full functionality, especially for weather-related features which are currently placeholders.

## Collaboration

Feel free to fork or clone the repository for further development. Contributions, bug reports, and feature requests are welcome!