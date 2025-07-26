from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import TypedDict, List
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from tavily import TavilyClient
import os
import requests
import json
from enum import Enum
load_dotenv()
# LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Tavily client
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


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


class GeneratedIdeatorState(TypedDict):
    topic: str
    max_ideators: int
    ideators: list[Ideator]
    research_results: list[ResearchResult]
    final_script: VideoScript


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
        print(f"🔍 {ideator.name} is conducting research...")
        
        # Generate search query based on persona
        query_prompt = search_query_instructions.format(
            persona=ideator.persona,
            topic=topic
        )
        
        search_query = query_llm.invoke([
            SystemMessage(content=query_prompt),
            HumanMessage(content="Generate your search query.")
        ])
        
        print(f"   Search query: {search_query.query}")
        print(f"   Chosen search method: {search_query.search_method.value}")
        print(f"   Reasoning: {search_query.reasoning}")
        
        # Conduct web search
        search_results = execute_search(search_query.query, search_query.search_method)
        
        print(f"🌐 Search Results Found:")
        print(search_results)
        print("\n" + "-"*50 + "\n")
        
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


script_instructions = """
You are an expert video script writer specializing in viral short-form content. Your task is to synthesize research insights from multiple ideators and create a compelling video script.

Topic: {topic}

Research Insights from Ideators:
{research_summary}

Create a video script that:
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
"""


def create_script(state: GeneratedIdeatorState):
    """Create a video script based on all research insights"""
    topic = state['topic']
    research_results = state['research_results']
    
    # Summarize all research insights
    research_summary = ""
    for result in research_results:
        research_summary += f"\n{result.ideator.name} ({result.ideator.role}):\n"
        research_summary += f"Search Method: {result.search_query.search_method.value}\n"
        research_summary += f"Key Insights: {result.key_insights}\n"
        research_summary += "-" * 40 + "\n"
    
    # Enforce structured output
    structured_llm = llm.with_structured_output(VideoScript)
    
    # System message
    system_message = script_instructions.format(
        topic=topic,
        research_summary=research_summary
    )
    
    # Generate script
    script = structured_llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content="Create the video script based on all the research insights.")
    ])
    
    return {"final_script": script}


if __name__ == "__main__":
    # Graph
    workflow = StateGraph(GeneratedIdeatorState)

    # Add nodes
    workflow.add_node("create_ideators", create_ideators)
    workflow.add_node("conduct_research", conduct_research)
    workflow.add_node("create_script", create_script)

    # Set entry point and edges
    workflow.set_entry_point("create_ideators")
    workflow.add_edge("create_ideators", "conduct_research")
    workflow.add_edge("conduct_research", "create_script")
    workflow.add_edge("create_script", END)

    # Compile
    graph = workflow.compile()

    # Input
    max_ideators = 3
    topic = "特斯拉財報發布"

    # Run the graph
    for event in graph.stream({"topic": topic, "max_ideators": max_ideators}, stream_mode="values"):
        # Review research results
        research_results = event.get('research_results', [])
        if research_results:
            print("\n" + "="*80)
            print("RESEARCH RESULTS")
            print("="*80)
            
            for result in research_results:
                print(f"\n🎭 IDEATOR: {result.ideator.name}")
                print(f"Role: {result.ideator.role}")
                print(f"Description: {result.ideator.description}")
                print(f"\n🔍 SEARCH QUERY: {result.search_query.query}")
                print(f"Reasoning: {result.search_query.reasoning}")
                print(f"\n💡 KEY INSIGHTS:")
                print(result.key_insights)
                print("-" * 80)
        
        # Review final script
        final_script = event.get('final_script')
        if final_script:
            print("\n" + "="*80)
            print("📝 FINAL VIDEO SCRIPT")
            print("="*80)
            print(f"\n🎬 TITLE: {final_script.title}")
            print(f"\n⚡ HOOK: {final_script.hook}")
            print(f"\n📖 MAIN CONTENT:\n{final_script.main_content}")
            print(f"\n📢 CALL TO ACTION: {final_script.call_to_action}")
            print(f"\n🎨 VISUAL SUGGESTIONS:\n{final_script.visual_suggestions}")
            print(f"\n⏱️ ESTIMATED DURATION: {final_script.estimated_duration}")
            print(f"\n📱 TARGET PLATFORMS: {', '.join(final_script.target_platforms)}")
            print("="*80)



