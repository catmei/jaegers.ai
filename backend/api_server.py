from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Generate video structure from topic via LangGraph dev API"""
    try:
        # Get topic from request
        data = request.get_json()
        if not data or 'topic' not in data:
            return jsonify({'error': 'Topic is required in request body'}), 400
        
        topic = data['topic']
        max_ideators = data.get('max_ideators', 3)  # Default to 3
        
        print(f"🎬 Processing topic: {topic}")
        print(f"📊 Max ideators: {max_ideators}")
        
        # LangGraph dev API endpoint
        langgraph_dev_url = "http://localhost:2024"
        
        # Step 1: Create a thread
        thread_url = f"{langgraph_dev_url}/threads"
        thread_response = requests.post(thread_url, json={"metadata": {}})
        
        if thread_response.status_code != 200:
            error_msg = f"Failed to create thread: {thread_response.status_code} - {thread_response.text}"
            print(f"❌ {error_msg}")
            return jsonify({'error': error_msg}), 500
        
        thread_id = thread_response.json()["thread_id"]
        print(f"🧵 Created thread: {thread_id}")
        
        # Step 2: Prepare the input for the LangGraph dev API
        input_data = {
            "topic": topic,
            "max_ideators": max_ideators
        }
        
        # Step 3: Call LangGraph dev API to stream the graph execution
        stream_url = f"{langgraph_dev_url}/threads/{thread_id}/runs/stream"
        
        payload = {
            "assistant_id": "ClipHunt",
            "input": input_data,
            "stream_mode": ["values"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        print(f"🚀 Calling LangGraph dev API at {stream_url}")
        
        # Step 4: Make streaming request to LangGraph dev API
        final_result = None
        with requests.post(stream_url, json=payload, headers=headers, stream=True) as response:
            if response.status_code != 200:
                error_msg = f"LangGraph dev API error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return jsonify({'error': error_msg}), 500
            
            # Process streaming response (SSE format)
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    # SSE format: "data: {json_data}"
                    if line_str.startswith('data: '):
                        try:
                            data_str = line_str[6:]  # Remove "data: " prefix
                            if data_str.strip():
                                event_data = json.loads(data_str)
                                
                                # Look for the final video structure in the event data
                                if isinstance(event_data, dict):
                                    final_video_structure = event_data.get('final_video_structure')
                                    if final_video_structure:
                                        final_result = final_video_structure
                                        print(f"📹 Received final video structure")
                        except json.JSONDecodeError:
                            # Skip lines that aren't valid JSON
                            continue
        
        if final_result is None:
            return jsonify({'error': 'Failed to generate video structure - no final result received'}), 500
        
        print(f"✅ Successfully generated video structure for: {topic}")
        return jsonify(final_result)
        
    except requests.exceptions.ConnectionError:
        error_msg = "Could not connect to LangGraph dev server. Make sure 'langgraph dev' is running on port 2024."
        print(f"❌ {error_msg}")
        return jsonify({'error': error_msg}), 503
        
    except Exception as e:
        print(f"❌ Error processing request: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Video generation API is running'})

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'Video Generation API (LangGraph Dev Wrapper)',
        'description': 'This API wraps the LangGraph dev server to enable LangSmith tracking',
        'prerequisites': 'Make sure LangGraph dev server is running on port 2024',
        'endpoints': {
            'POST /generate-video': 'Generate video structure from topic via LangGraph dev API',
            'GET /health': 'Health check',
            'GET /': 'This information'
        },
        'example_usage': {
            'curl': 'curl -X POST http://localhost:5001/generate-video -H "Content-Type: application/json" -d \'{"topic": "lebron james and the lakers"}\'',
            'setup': [
                '1. Start LangGraph dev: cd backend/agent && langgraph dev',
                '2. Start this API: python backend/api_server.py',
                '3. Make requests to this API which will forward to LangGraph dev'
            ]
        }
    })