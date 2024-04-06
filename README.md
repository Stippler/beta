# Calendar App API

This FastAPI application serves as the backend for a calendar app, enabling the creation and management of tasks/events with consideration for weather conditions. It's designed to quickly set up an extendable API for a hackathon project using Next.js for the frontend.

## Features

- Create tasks with title, timeframe, and location.
- List all created tasks.
- Analyze natural text for task creation feasibility.
- Retrieve weather data based on longitude, latitude, and timeframe.
- Check if the weather conditions are suitable for the scheduled tasks.

## Endpoints

- `POST /task/`: Create a new task.
    - Input: `{ "title": "string", "timeframe": "string", "location": "string" }`
    - Output: `{"result": "yes/no"}`
- `GET /task/`: List all tasks.
    - Output: List of tasks.
- `POST /text/`: Analyze natural text for task creation.
    - Input: `{ "text": "string" }`
    - Output: `{"result": "yes/no"}`
- `POST /weather/`: Get weather data for a location and timeframe.
    - Input: `{ "longitude": float, "latitude": float, "timeframe": "string" }`
    - Output: List of `{"temperature": float, "humidity": float}`
- `POST /ok/`: Check if weather conditions are suitable for the event.
    - Input: `{ "longitude": float, "latitude": float, "timeframe": "string" }`
    - Output: `{"result": "yes/no"}`

## Setup and Run

1. **Install Dependencies**:
   - Ensure you have Python installed on your system.
   - Install FastAPI and Uvicorn with pip:
     ```
     pip install fastapi uvicorn
     ```

2. **Running the Application**:
   - Save the provided API script as `api.py`.
   - Start the server using Uvicorn:
     ```
     uvicorn api:app --reload
     ```
   - The API will be available at `http://localhost:8000`.

## Extending the API

To further develop this API for a production environment, consider the following:

- **Weather API Integration**: Implement real-time weather data fetching from a service like OpenWeatherMap for the `/weather` and `/ok` endpoints.
- **NLP for Text Analysis**: Use libraries like NLTK or SpaCy, or external services for analyzing natural text in the `/text` endpoint.
- **Database Integration**: Replace the in-memory storage with a database solution for persistent data management.

## Collaboration

Feel free to fork or clone the repository for further development. Contributions, bug reports, and feature requests are welcome!