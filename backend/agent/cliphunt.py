from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import TypedDict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from tavily import TavilyClient
from google import genai
from google.genai import types
import os
import requests
from enum import Enum
from googleapiclient.discovery import build


load_dotenv()
# LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

# Tavily client
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Google Gemini client
gemini_client = genai.Client()

# YouTube API client
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
if youtube_api_key:
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
else:
    youtube = None


class SearchMethod(str, Enum):
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    REDDIT_STYLE = "reddit_style"
    NEWS_FOCUSED = "news_focused"


class Ideator(BaseModel):
    name: str = Field(
        description="Name of the ideator."
    )
    role: str = Field(
        description="Role of the ideator in the context of the topic.",
    )
    description: str = Field(
        description="Description of the ideator focus, concerns, and motives.",
    )
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nDescription: {self.description}\n"


class SearchQuery(BaseModel):
    query: str = Field(
        description="Search query tailored to the ideator's perspective and interests."
    )
    search_method: SearchMethod = Field(
        description="The search method/API that would be most effective for this type of research."
    )
    reasoning: str = Field(
        description="Why this search query and method aligns with the ideator's persona and what they hope to find."
    )


class ResearchResult(BaseModel):
    ideator: Ideator
    search_query: SearchQuery
    search_results: str = Field(
        description="Raw search results from the web search."
    )
    key_insights: str = Field(
        description="Key insights extracted from the search results that align with the ideator's interests."
    )
    

class Perspectives(BaseModel):
    ideators: List[Ideator] = Field(
        description="Comprehensive list of ideators with their roles and descriptions.",
    )


class VideoScript(BaseModel):
    title: str = Field(
        description="Compelling title for the short-form video."
    )
    hook: str = Field(
        description="Opening hook to grab attention in the first 3 seconds."
    )
    main_content: str = Field(
        description="Main story/content structure with timestamps and key points."
    )
    call_to_action: str = Field(
        description="Strong ending call-to-action or memorable conclusion."
    )
    visual_suggestions: str = Field(
        description="Suggestions for visuals, graphics, or footage to accompany the script."
    )
    estimated_duration: str = Field(
        description="Estimated video duration (e.g., '30-45 seconds')."
    )
    target_platforms: List[str] = Field(
        description="Recommended platforms for this content (TikTok, Instagram Reels, YouTube Shorts, etc.)."
    )


class TimestampKeywords(BaseModel):
    timestamp: str = Field(
        description="The timestamp from the script (e.g., '[0-5 seconds]')."
    )
    content_line: str = Field(
        description="The full content line for this timestamp."
    )
    keywords: List[str] = Field(
        description="List of important keywords, names, concepts, or entities extracted from this line."
    )


class KeywordExtraction(BaseModel):
    timestamp_keywords: List[TimestampKeywords] = Field(
        description="List of keywords extracted for each timestamped line in the video script."
    )


class ContentSearchResult(BaseModel):
    title: str = Field(
        description="Title or description of the found content."
    )
    timestamp: str = Field(
        description="The timestamp this search corresponds to."
    )
    keywords: List[str] = Field(
        description="List of keywords that were searched together."
    )
    search_query: str = Field(
        description="The actual search query used."
    )
    links: List[str] = Field(
        description="List of relevant YouTube URLs or links to the content."
    )


class ContentSearchResults(BaseModel):
    search_results: List[ContentSearchResult] = Field(
        description="List of search results for each timestamp."
    )


class VideoUnderstandingResult(BaseModel):
    timestamp: str = Field(
        description="The timestamp this analysis corresponds to."
    )
    keywords: List[str] = Field(
        description="Keywords used for analysis."
    )
    youtube_url: str = Field(
        description="The YouTube URL that was analyzed."
    )
    analysis_query: str = Field(
        description="The query used for video analysis."
    )
    analysis_result: str = Field(
        description="The detailed analysis result from Gemini in JSON format."
    )
    processing_time: float = Field(
        description="Time taken to process the video in seconds."
    )


class VideoSegment(BaseModel):
    timestamp: str = Field(
        description="Video timestamp (e.g., '00:07', '00:14')."
    )
    content: str = Field(
        description="Description of what happens at this timestamp."
    )


class ParsedVideoAnalysis(BaseModel):
    script_timestamp: str = Field(
        description="The original script timestamp (e.g., '[0-5 seconds]')."
    )
    keywords: List[str] = Field(
        description="Keywords used for analysis."
    )
    youtube_url: str = Field(
        description="The YouTube URL that was analyzed."
    )
    video_segments: List[VideoSegment] = Field(
        description="Parsed video segments with individual timestamps."
    )
    processing_time: float = Field(
        description="Time taken to process the video in seconds."
    )


class ParsedVideoAnalysisResults(BaseModel):
    parsed_results: List[ParsedVideoAnalysis] = Field(
        description="List of parsed video analysis results."
    )


class VideoUnderstandingResults(BaseModel):
    understanding_results: List[VideoUnderstandingResult] = Field(
        description="List of video understanding results for each timestamp."
    )


class VisualElement(BaseModel):
    sub_time_range: str = Field(
        description="Sub time range for this visual element."
    )
    type: str = Field(
        description="Type of visual: 'concept' or 'clip'."
    )
    source: Optional[str] = Field(
        description="Source information including platform, url, and time_range, or null for concept visuals."
    )
    description: str = Field(
        description="Description of the visual content."
    )


class Segment(BaseModel):
    time_range: str = Field(
        description="Time range for this segment."
    )
    title: str = Field(
        description="Title of the segment."
    )
    visual: List[VisualElement] = Field(
        description="List of visual elements for this segment."
    )
    audio: str = Field(
        description="Audio description for this segment."
    )


class FinalVideoStructure(BaseModel):
    title: str = Field(
        description="Title of the video script."
    )
    goal: str = Field(
        description="Goal and purpose of the video."
    )
    style: List[str] = Field(
        description="List of style descriptors."
    )
    segments: List[Segment] = Field(
        description="List of segments with detailed visual and audio information."
    )


class Scriptor(BaseModel):
    name: str = Field(
        description="Name of the scriptor."
    )
    specialization: str = Field(
        description="Specialization in video script writing (e.g., viral content, storytelling, educational content)."
    )
    writing_style: str = Field(
        description="Description of the scriptor's writing style and approach."
    )
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nSpecialization: {self.specialization}\nWriting Style: {self.writing_style}\n"


class GeneratedIdeatorState(TypedDict):
    topic: str
    max_ideators: int
    ideators: list[Ideator]
    research_results: list[ResearchResult]
    scriptor: Scriptor
    final_script: VideoScript
    keyword_extraction: KeywordExtraction
    content_search_results: ContentSearchResults
    video_understanding_results: VideoUnderstandingResults
    parsed_video_analysis: ParsedVideoAnalysisResults
    final_video_structure: FinalVideoStructure


ideator_instructions="""
You are tasked with creating a set of AI ideator personas. Each ideator should be an expert in short-form video creation, with the following core responsibilities:

核心職責 (Core Responsibilities):
- 分析市場趨勢、受眾喜好和熱門話題 (Analyze market trends, audience preferences, and popular topics).
- 從大量數據中提煉出新穎的影片題材、故事線索或概念 (Extract novel video subjects, storylines, or concepts from large amounts of data).
- 根據客戶需求或目標，生成多個創意方向或提案大綱 (Generate multiple creative directions or proposal outlines based on client requirements or goals).
- 對既有概念進行迭代和優化，找出潛在亮點 (Iterate and optimize existing concepts to identify potential highlights).

Follow these instructions to generate the personas:
1. First, review the research topic:
{topic}
   
2. Determine the most interesting themes based upon the topic and the core responsibilities.
                    
3. Pick the top {max_ideators} themes.

4. For each theme, assign an ideator persona whose role and description are tailored to that theme and embody the core responsibilities."""


search_query_instructions = """
Based on your persona and the research topic, generate a specific search query AND choose the most appropriate search method that would help you find the most relevant and interesting information for creating short-form video content.

Your Persona:
{persona}

Research Topic: {topic}

Available Search Methods:
1. TAVILY - Comprehensive web search with detailed content extraction (best for in-depth research)
2. DUCKDUCKGO - General web search with quick results (good for broad topic exploration)
3. REDDIT_STYLE - Focus on discussions, opinions, and community insights (great for understanding public sentiment)
4. NEWS_FOCUSED - Recent news and current events (perfect for trending topics and breaking news)

Generate a search query and choose a method that:
1. Reflects your unique perspective and expertise
2. Will help you find information that aligns with your specific interests and role
3. Could lead to creative video content ideas
4. Takes advantage of the most suitable search approach for your research goals

Be strategic about both WHAT you search for and HOW you search - think about what search method would be most valuable for your specific role in video content creation."""


scriptor_instructions = """
You are tasked with creating a specialized video script writer persona. This scriptor will be responsible for combining insights from multiple ideators and creating compelling short-form video scripts.

Topic: {topic}

Create a scriptor persona that:
1. Has expertise in viral short-form video content
2. Can synthesize multiple perspectives into one cohesive narrative
3. Understands platform-specific requirements (TikTok, Instagram Reels, YouTube Shorts)
4. Has a unique writing style that would work well for this topic

The scriptor should NOT conduct research - they focus purely on script creation using the research provided by ideators.
"""


def tavily_search(query: str) -> str:
    """Search using Tavily API for comprehensive results"""
    try:
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )
        
        results = []
        if 'results' in response:
            for result in response['results']:
                title = result.get('title', 'No title')
                content = result.get('content', 'No content')
                url = result.get('url', 'No URL')
                results.append(f"Title: {title}\nContent: {content}\nURL: {url}")
        
        return "\n\n".join(results) if results else "No search results found"
        
    except Exception as e:
        return f"Tavily search error: {str(e)}"


def duckduckgo_search(query: str) -> str:
    """Search using DuckDuckGo API for general web results"""
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        results = []
        if 'Results' in data and data['Results']:
            for result in data['Results'][:5]:
                results.append(f"Title: {result.get('Text', '')}\nURL: {result.get('FirstURL', '')}")
        
        if 'RelatedTopics' in data and data['RelatedTopics']:
            for topic in data['RelatedTopics'][:3]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append(f"Related: {topic['Text']}")
        
        return "\n\n".join(results) if results else "No DuckDuckGo results found"
        
    except Exception as e:
        return f"DuckDuckGo search error: {str(e)}"


def reddit_style_search(query: str) -> str:
    """Search focusing on discussion-style content and social insights"""
    try:
        # Use Tavily with Reddit-focused query modification
        reddit_query = f"{query} site:reddit.com OR discussion OR opinion OR community"
        response = tavily.search(
            query=reddit_query,
            search_depth="basic",
            max_results=4
        )
        
        results = []
        if 'results' in response:
            for result in response['results']:
                title = result.get('title', 'No title')
                content = result.get('content', 'No content')
                url = result.get('url', 'No URL')
                results.append(f"Discussion: {title}\nContent: {content}\nSource: {url}")
        
        return "\n\n".join(results) if results else "No discussion results found"
        
    except Exception as e:
        return f"Reddit-style search error: {str(e)}"


def news_focused_search(query: str) -> str:
    """Search focusing on recent news and current events"""
    try:
        # Use Tavily with news-focused parameters
        news_query = f"{query} news OR latest OR recent OR breaking"
        response = tavily.search(
            query=news_query,
            search_depth="basic",
            max_results=5,
            include_domains=["cnn.com", "bbc.com", "reuters.com", "ap.org", "npr.org"]
        )
        
        results = []
        if 'results' in response:
            for result in response['results']:
                title = result.get('title', 'No title')
                content = result.get('content', 'No content')
                url = result.get('url', 'No URL')
                results.append(f"News: {title}\nContent: {content}\nSource: {url}")
        
        return "\n\n".join(results) if results else "No news results found"
        
    except Exception as e:
        return f"News search error: {str(e)}"


def execute_search(query: str, method: SearchMethod) -> str:
    """Execute search using the specified method"""
    search_functions = {
        SearchMethod.TAVILY: tavily_search,
        SearchMethod.DUCKDUCKGO: duckduckgo_search,
        SearchMethod.REDDIT_STYLE: reddit_style_search,
        SearchMethod.NEWS_FOCUSED: news_focused_search,
    }
    
    search_func = search_functions.get(method, tavily_search)
    return search_func(query)


def create_ideators(state: GeneratedIdeatorState):
    """ Create ideators """
    topic = state['topic']
    max_ideators = state['max_ideators']
    
    # Enforce structured output
    structured_llm = llm.with_structured_output(Perspectives)

    # System message
    system_message = ideator_instructions.format(topic=topic, max_ideators=max_ideators)

    # Generate ideators
    ideators = structured_llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Generate the set of ideators.")])
    
    # Write the list of ideators to state
    return {"ideators": ideators.ideators}


def conduct_research(state: GeneratedIdeatorState):
    """ Each ideator conducts web research based on their persona """
    ideators = state['ideators']
    topic = state['topic']
    research_results = []
    
    # Structured LLM for generating search queries
    query_llm = llm.with_structured_output(SearchQuery)
    
    for ideator in ideators:        
        # Generate search query based on persona
        query_prompt = search_query_instructions.format(
            persona=ideator.persona,
            topic=topic
        )
        
        search_query = query_llm.invoke([
            SystemMessage(content=query_prompt),
            HumanMessage(content="Generate your search query.")
        ])
    
        # Conduct web search
        search_results = execute_search(search_query.query, search_query.search_method)
    
        # Generate insights from search results
        insights_prompt = f"""
        As {ideator.name} ({ideator.role}), analyze these search results and extract key insights that are most relevant to your expertise and interests for creating short-form video content about "{topic}".

        Search Results:
        {search_results}

        Focus on:
        1. Information that aligns with your specific role and perspective
        2. Trends, stories, or angles that could make compelling video content
        3. Unique insights that other personas might miss
        4. Actionable content ideas or creative directions

        Provide your key insights:
        """
        
        insights = llm.invoke([
            SystemMessage(content=f"You are {ideator.name}, a {ideator.role}. {ideator.description}"),
            HumanMessage(content=insights_prompt)
        ]).content
        
        # Create research result
        research_result = ResearchResult(
            ideator=ideator,
            search_query=search_query,
            search_results=search_results,
            key_insights=insights
        )
        
        research_results.append(research_result)
    
    return {"research_results": research_results}


def create_scriptor(state: GeneratedIdeatorState):
    """Create a specialized scriptor for writing the video script"""
    topic = state['topic']
        
    # Enforce structured output
    structured_llm = llm.with_structured_output(Scriptor)
    
    # System message
    system_message = scriptor_instructions.format(topic=topic)
    
    # Generate scriptor
    scriptor = structured_llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content="Generate the scriptor persona.")
    ])
    
    return {"scriptor": scriptor}


def create_script(state: GeneratedIdeatorState):
    """Scriptor creates a video script based on all research insights"""
    topic = state['topic']
    research_results = state['research_results']
    scriptor = state['scriptor']
    
    # Summarize all research insights
    research_summary = ""
    for result in research_results:
        research_summary += f"\n{result.ideator.name} ({result.ideator.role}):\n"
        research_summary += f"Search Method: {result.search_query.search_method.value}\n"
        research_summary += f"Key Insights: {result.key_insights}\n"
        research_summary += "-" * 40 + "\n"
    
    # Enforce structured output
    structured_llm = llm.with_structured_output(VideoScript)
    
    # Updated system message with scriptor persona
    system_message = f"""
You are {scriptor.name}, a {scriptor.specialization}. {scriptor.writing_style}

Your task is to synthesize research insights from multiple ideators and create a compelling video script.

Topic: {topic}

Research Insights from Ideators:
{research_summary}

As {scriptor.name}, create a video script that:
1. Starts with a POWERFUL HOOK that grabs attention in the first 3 seconds
2. Tells a compelling story or presents information in an engaging way
3. Incorporates the most interesting insights from the research
4. Includes specific timing cues for a short-form video (15-60 seconds)
5. Ends with a strong call-to-action or memorable conclusion
6. Suggests appropriate visuals to accompany the content

Focus on:
- Making it immediately engaging and shareable
- Using the unique angles discovered by the ideators
- Optimizing for short attention spans
- Creating emotional impact or providing clear value
- Applying your unique writing style and specialization
"""
    
    # Generate script
    script = structured_llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content="Create the video script based on all the research insights.")
    ])
    
    return {"final_script": script}


def extract_keywords(state: GeneratedIdeatorState):
    """Extract keywords from each timestamped line in the video script's main content"""
    final_script = state['final_script']
    topic = state['topic']
    
    # Parse the main_content to find timestamped lines
    main_content = final_script.main_content
    lines = main_content.split('\n')
    
    # Find lines that contain timestamps (looking for patterns like [X-Y seconds] or [X seconds])
    timestamped_lines = []
    for line in lines:
        line = line.strip()
        if line and ('[' in line and 'second' in line and ']' in line):
            timestamped_lines.append(line)
    
    # If no timestamped lines found, treat the entire main_content as one block
    if not timestamped_lines:
        timestamped_lines = [main_content]
    
    # Enforce structured output for keyword extraction
    structured_llm = llm.with_structured_output(KeywordExtraction)
    
    # Create the prompt for keyword extraction
    lines_text = "\n".join([f"Line {i+1}: {line}" for i, line in enumerate(timestamped_lines)])
    
    system_message = f"""
You are an expert at analyzing video script content to extract important keywords for YouTube.

Topic: {topic}

Task: For each timestamped line from the video script, extract 1-3 highly useful YouTube keywords. 
These keywords should capture primary visual subjects, key actions, central concepts, 
and relevant proper nouns for finding related video content. Prioritize specific, impactful, and directly searchable terms.

Extraction Focus (3-8 keywords per line):

People's names 

Organizations/Entities 

Key concepts/Themes 

Important objects, places, or events

Text overlays or visual elements mentioned

Prioritize: Proper nouns, key thematic concepts, prominent visual elements, and terms capturing the essence of the moment.

Timestamped Lines to Analyze:
{lines_text}
"""
    
    # Generate keyword extraction
    keyword_extraction = structured_llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content="Extract the keywords from each timestamped line.")
    ])
    
    return {"keyword_extraction": keyword_extraction}


def search_youtube_api(state: GeneratedIdeatorState):
    """Search for content using YouTube API with extracted keywords by timestamp structure"""
    keyword_extraction = state['keyword_extraction']
    topic = state['topic']
    
    if not youtube:
        return {"content_search_results": ContentSearchResults(search_results=[])}
    
    search_results = []
    
    # Process each timestamp separately
    for timestamp_keyword in keyword_extraction.timestamp_keywords:
        timestamp = timestamp_keyword.timestamp
        keywords = timestamp_keyword.keywords
        
        # Combine keywords for search
        search_query = " ".join(keywords) + " " + topic
                
        try:
            # Search YouTube using the API
            search_response = youtube.search().list(
                q=search_query,
                part='id,snippet',
                maxResults=5,
                type='video',
                order='relevance'
            ).execute()
            
            video_links = []
            video_titles = []
            
            for search_result in search_response.get('items', []):
                video_id = search_result['id']['videoId']
                video_title = search_result['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                video_links.append(video_url)
                video_titles.append(video_title)
            
            # Create a descriptive title
            content_title = f"YouTube API results for {timestamp} - Found {len(video_links)} videos"
            
            # Create search result
            search_result = ContentSearchResult(
                title=content_title,
                timestamp=timestamp,
                keywords=keywords,
                search_query=search_query,
                links=video_links
            )
            
            search_results.append(search_result)
            
        except Exception as e:            # Create a fallback result even if search fails
            search_result = ContentSearchResult(
                title=f"YouTube API search failed for {timestamp}",
                timestamp=timestamp,
                keywords=keywords,
                search_query=search_query,
                links=[]
            )
            search_results.append(search_result)
    
    content_search_results = ContentSearchResults(search_results=search_results)    
    return {"content_search_results": content_search_results}


def understand_youtube_videos(state: GeneratedIdeatorState):
    """Analyze YouTube videos using Gemini's understanding API with extracted keywords"""
    content_search_results = state['content_search_results']
    topic = state['topic']
    
    understanding_results = []
    
    # Process only the FIRST search result
    if content_search_results.search_results:
        search_result = content_search_results.search_results[0]  # Only first result
        timestamp = search_result.timestamp
        keywords = search_result.keywords
        
        # Get the first YouTube URL for analysis
        youtube_url = None
        if search_result.links:
            youtube_url = search_result.links[0] # Only first video
        
        if not youtube_url:
            print(f"No YouTube URL found for timestamp {timestamp}, skipping...")
        else:            
            try:
                import time
                start_time = time.time()
                
                # Create analysis query based on keywords and topic
                keywords_text = ", ".join(keywords)

                analysis_query = f"Please analyze this video for segments related to '{keywords_text}' and '{topic}'. Identify all timestamps where these keywords are mentioned, providing the time in minutes and seconds, along with a brief description of the content within that segment. Please return the information in JSON format, including the timestamp and content description."
                
                # Use Gemini's understanding API
                response = gemini_client.models.generate_content(
                    model='models/gemini-2.5-flash',
                    contents=types.Content(
                        parts=[
                            types.Part(
                                file_data=types.FileData(file_uri=youtube_url),
                            ),
                            types.Part(text=analysis_query)
                        ]
                    )
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                analysis_result = response.text
                                
                # Create understanding result
                understanding_result = VideoUnderstandingResult(
                    timestamp=timestamp,
                    keywords=keywords,
                    youtube_url=youtube_url,
                    analysis_query=analysis_query,
                    analysis_result=analysis_result,
                    processing_time=processing_time
                )
                
                understanding_results.append(understanding_result)
                
            except Exception as e:                # Create a fallback result even if analysis fails
                understanding_result = VideoUnderstandingResult(
                    timestamp=timestamp,
                    keywords=keywords,
                    youtube_url=youtube_url or "No URL available",
                    analysis_query=analysis_query if 'analysis_query' in locals() else "Query not generated",
                    analysis_result=f"Analysis failed: {str(e)}",
                    processing_time=0.0
                )
                understanding_results.append(understanding_result)
    
    video_understanding_results = VideoUnderstandingResults(understanding_results=understanding_results)    
    return {"video_understanding_results": video_understanding_results}


def parse_video_analysis(state: GeneratedIdeatorState):
    """Parse video understanding results to extract individual video segments with timestamps"""
    video_understanding_results = state['video_understanding_results']
    parsed_results = []
    
    for understanding_result in video_understanding_results.understanding_results:
        try:
            # Extract JSON from markdown code blocks if present
            analysis_text = understanding_result.analysis_result.strip()
            
            # Check if the response is wrapped in markdown code blocks
            if analysis_text.startswith('```json') or analysis_text.startswith('```'):
                # Extract content between ```json and ```
                lines = analysis_text.split('\n')
                json_lines = []
                in_json_block = False
                
                for line in lines:
                    if line.strip().startswith('```json') or line.strip() == '```':
                        in_json_block = True
                        continue
                    elif line.strip() == '```' and in_json_block:
                        break
                    elif in_json_block:
                        json_lines.append(line)
                
                json_text = '\n'.join(json_lines)
            else:
                json_text = analysis_text
            
            # Parse the JSON analysis result
            import json
            analysis_data = json.loads(json_text)
            
            # Extract video segments
            video_segments = []
            if isinstance(analysis_data, list):
                for segment_data in analysis_data:
                    if 'timestamp' in segment_data and 'content' in segment_data:
                        video_segment = VideoSegment(
                            timestamp=segment_data['timestamp'],
                            content=segment_data['content']
                        )
                        video_segments.append(video_segment)
            
            # Create parsed analysis
            parsed_analysis = ParsedVideoAnalysis(
                script_timestamp=understanding_result.timestamp,
                keywords=understanding_result.keywords,
                youtube_url=understanding_result.youtube_url,
                video_segments=video_segments,
                processing_time=understanding_result.processing_time
            )
            
            parsed_results.append(parsed_analysis)
                        
        except json.JSONDecodeError as e:
            # Create a fallback with no segments
            parsed_analysis = ParsedVideoAnalysis(
                script_timestamp=understanding_result.timestamp,
                keywords=understanding_result.keywords,
                youtube_url=understanding_result.youtube_url,
                video_segments=[],
                processing_time=understanding_result.processing_time
            )
            parsed_results.append(parsed_analysis)
        
        except Exception as e:            # Create a fallback with no segments
            parsed_analysis = ParsedVideoAnalysis(
                script_timestamp=understanding_result.timestamp,
                keywords=understanding_result.keywords,
                youtube_url=understanding_result.youtube_url,
                video_segments=[],
                processing_time=understanding_result.processing_time
            )
            parsed_results.append(parsed_analysis)
    
    parsed_video_analysis = ParsedVideoAnalysisResults(parsed_results=parsed_results)
        
    return {"parsed_video_analysis": parsed_video_analysis}


def generate_final_structure(state: GeneratedIdeatorState):
    """Generate the final structured JSON using all previous state data"""
    final_script = state['final_script']
    keyword_extraction = state['keyword_extraction']
    content_search_results = state['content_search_results']
    parsed_video_analysis = state['parsed_video_analysis']
    topic = state['topic']
        
    # Create segments based on actual data
    segments = []
    
    # Process each timestamp from keyword extraction
    for i, timestamp_keyword in enumerate(keyword_extraction.timestamp_keywords):
        timestamp = timestamp_keyword.timestamp
        keywords = timestamp_keyword.keywords
        content_line = timestamp_keyword.content_line
        
        # Find corresponding search result
        search_result = None
        if i < len(content_search_results.search_results):
            search_result = content_search_results.search_results[i]
        
        # Create visual elements
        visual_elements = []
        
        # Find corresponding parsed video analysis for this script timestamp
        matching_parsed_analysis = None
        for parsed_analysis in parsed_video_analysis.parsed_results:
            if parsed_analysis.script_timestamp == timestamp:
                matching_parsed_analysis = parsed_analysis
                break
        
        # Add visual elements from parsed video analysis
        if matching_parsed_analysis and matching_parsed_analysis.video_segments:
            for video_segment in matching_parsed_analysis.video_segments:
                visual_element = VisualElement(
                    sub_time_range=video_segment.timestamp,  # Use the actual video timestamp
                    type="clip",
                    source=matching_parsed_analysis.youtube_url,
                    description=video_segment.content
                )
                visual_elements.append(visual_element)
        
        # If no video analysis results, create a concept visual
        if not visual_elements:
            visual_element = VisualElement(
                sub_time_range=timestamp,
                type="concept",
                source=None,
                description=f"Visual concept for: {content_line}"
            )
            visual_elements.append(visual_element)
        
        # Create segment
        segment = Segment(
            time_range=timestamp,
            title=f"Segment: {', '.join(keywords)}",
            visual=visual_elements,
            audio="Background music and narration"
        )
        
        segments.append(segment)
    
    # Create the final structure
    final_structure = FinalVideoStructure(
        title=final_script.title,
        goal=f"Create engaging short-form content about {topic} using insights from research and video analysis",
        style=["informative", "engaging", "dynamic"],
        segments=segments
    )
        
    return {"final_video_structure": final_structure}


# Graph
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

# Compile
graph = workflow.compile()

# Reference Input: initial_state = {"topic": "lebron james and the lakers", "max_ideators": 1}