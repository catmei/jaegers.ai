# Video Generation API (Backend)

A Flask-based API server that generates video structures from topics using AI-powered research and analysis.

## Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Copy `.env_example` to `.env` in the **root** directory and fill in your API keys:
   ```bash
   cp ../.env_example ../.env
   # Edit ../.env with your API keys
   ```

4. **Start the API server:**
   ```bash
   python run_api.py
   ```

The server will start at `http://localhost:5000`

## Project Structure

```
backend/
├── agent/             # AI agent workflow implementation
│   ├── agent.py       # Main workflow logic
│   └── debug.py       # Debug utilities
├── api_server.py      # Flask API server
├── run_api.py         # Server startup script
├── test_api.py        # API testing script
├── requirements.txt   # Backend dependencies
└── README_API.md      # This file
```

## API Endpoints

### POST /generate-video
Generate a video structure from a topic.

**Request:**
```bash
curl -X POST http://localhost:5000/generate-video \
  -H "Content-Type: application/json" \
  -d '{"topic": "lebron james and the lakers"}'
```

**Request Body:**
```json
{
  "topic": "your topic here",
  "max_ideators": 1  // optional, defaults to 1
}
```

**Response:**
```json
{
  "title": "Video Title",
  "goal": "Video goal and purpose",
  "style": ["informative", "engaging", "dynamic"],
  "segments": [
    {
      "time_range": "[0-5 seconds]",
      "title": "Segment title",
      "visual": [
        {
          "sub_time_range": "00:07",
          "type": "clip",
          "source": "https://youtube.com/watch?v=...",
          "description": "Visual description"
        }
      ],
      "audio": "Audio description"
    }
  ]
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Video generation API is running"
}
```

### GET /
API information and usage examples.

## Testing

Run the test script to verify the API is working:

```bash
cd backend
python test_api.py
```

## Example Usage

1. **Basic curl request:**
   ```bash
   curl -X POST http://localhost:5000/generate-video \
     -H "Content-Type: application/json" \
     -d '{"topic": "artificial intelligence trends"}'
   ```

2. **With custom ideator count:**
   ```bash
   curl -X POST http://localhost:5000/generate-video \
     -H "Content-Type: application/json" \
     -d '{"topic": "climate change solutions", "max_ideators": 3}'
   ```

3. **Save response to file:**
   ```bash
   curl -X POST http://localhost:5000/generate-video \
     -H "Content-Type: application/json" \
     -d '{"topic": "space exploration"}' \
     -o video_structure.json
   ```

## Response Structure

The API returns a comprehensive video structure with:

- **Title**: Compelling video title
- **Goal**: Purpose and objective of the video
- **Style**: List of style descriptors
- **Segments**: Array of time-based segments, each containing:
  - **time_range**: Timestamp for the segment
  - **title**: Segment title
  - **visual**: Array of visual elements with sources and descriptions
  - **audio**: Audio description

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (missing topic)
- `500`: Internal server error

Error responses include details:
```json
{
  "error": "Error description"
}
```

## Development

The backend uses:
- **Flask**: Web framework
- **LangGraph**: AI workflow orchestration
- **Google Gemini**: AI model for analysis
- **YouTube API**: Video content search
- **Tavily**: Web search capabilities

For the main project documentation, see [`../README.md`](../README.md). 