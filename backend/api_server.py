from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from agent.agent import (
    StateGraph, GeneratedIdeatorState, END,
    create_ideators, conduct_research, create_scriptor, create_script,
    extract_keywords, search_youtube_api, understand_youtube_videos,
    parse_video_analysis, generate_final_structure
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def create_video_workflow():
    """Create and compile the video generation workflow"""
    workflow = StateGraph(GeneratedIdeatorState)

    # Add nodes
    workflow.add_node("create_ideators", create_ideators)
    workflow.add_node("conduct_research", conduct_research)
    workflow.add_node("create_scriptor", create_scriptor)
    workflow.add_node("create_script", create_script)
    workflow.add_node("extract_keywords", extract_keywords)
    workflow.add_node("search_youtube_api", search_youtube_api)
    workflow.add_node("understand_youtube_videos", understand_youtube_videos)
    workflow.add_node("parse_video_analysis", parse_video_analysis)
    workflow.add_node("generate_final_structure", generate_final_structure)

    # Set entry point and edges
    workflow.set_entry_point("create_ideators")
    workflow.add_edge("create_ideators", "conduct_research")
    workflow.add_edge("conduct_research", "create_scriptor")
    workflow.add_edge("create_scriptor", "create_script")
    workflow.add_edge("create_script", "extract_keywords")
    workflow.add_edge("extract_keywords", "search_youtube_api")
    workflow.add_edge("search_youtube_api", "understand_youtube_videos")
    workflow.add_edge("understand_youtube_videos", "parse_video_analysis")
    workflow.add_edge("parse_video_analysis", "generate_final_structure")
    workflow.add_edge("generate_final_structure", END)

    return workflow.compile()

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Generate video structure from topic"""
    try:
        # Get topic from request
        data = request.get_json()
        if not data or 'topic' not in data:
            return jsonify({'error': 'Topic is required in request body'}), 400
        
        topic = data['topic']
        max_ideators = data.get('max_ideators', 1)  # Default to 1
        
        print(f"🎬 Processing topic: {topic}")
        print(f"📊 Max ideators: {max_ideators}")
        
        # Create and run the workflow
        graph = create_video_workflow()
        
        # Run the graph and collect final result
        final_result = None
        for event in graph.stream({"topic": topic, "max_ideators": max_ideators}, stream_mode="values"):
            final_video_structure = event.get('final_video_structure')
            if final_video_structure:
                final_result = final_video_structure
        
        if final_result is None:
            return jsonify({'error': 'Failed to generate video structure'}), 500
        
        # Convert Pydantic model to dict for JSON serialization
        result_dict = final_result.model_dump()
        print(result_dict)
        print(f"✅ Successfully generated video structure for: {topic}")
        return jsonify(result_dict)
        
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
        'message': 'Video Generation API',
        'endpoints': {
            'POST /generate-video': 'Generate video structure from topic',
            'GET /health': 'Health check',
            'GET /': 'This information'
        },
        'example_usage': {
            'curl': 'curl -X POST http://localhost:5001/generate-video -H "Content-Type: application/json" -d \'{"topic": "lebron james and the lakers"}\''
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Video Generation API Server...")
    print("📍 Server will be available at: http://localhost:5001")
    print("🔍 Health check: http://localhost:5001/health")
    print("📋 API info: http://localhost:5001/")
    print("\n💡 Example usage:")
    print('curl -X POST http://localhost:5001/generate-video -H "Content-Type: application/json" -d \'{"topic": "lebron james and the lakers"}\'')
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=True) 