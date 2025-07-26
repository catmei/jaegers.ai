import json
from typing import Any

class DebugPrinter:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
    
    def print_node_start(self, node_name: str, description: str = ""):
        """Print when a node starts executing"""
        if not self.enabled:
            return
        print(f"\n🔄 {node_name.upper().replace('_', ' ')}")
        if description:
            print(f"   {description}")
        print()
    
    def print_extraction_info(self, num_lines: int, lines_found: bool = True):
        """Print keyword extraction information"""
        if not self.enabled:
            return
        if lines_found:
            print(f"Found {num_lines} timestamped lines to process")
        else:
            print("No specific timestamps found, processing entire content as one block")
    
    def print_search_progress(self, timestamp: str, keywords: list, query: str):
        """Print search progress for each timestamp"""
        if not self.enabled:
            return
        print(f"🔎 Searching for timestamp {timestamp}")
        print(f"   Keywords: {', '.join(keywords)}")
        print(f"   Search query: {query}")
    
    def print_video_analysis_progress(self, timestamp: str, keywords: list, url: str):
        """Print video analysis progress"""
        if not self.enabled:
            return
        print(f"🔍 Analyzing video for timestamp {timestamp}")
        print(f"   Keywords: {', '.join(keywords)}")
        print(f"   YouTube URL: {url}")
    
    def print_analysis_complete(self, processing_time: float, preview: str):
        """Print when video analysis completes"""
        if not self.enabled:
            return
        print(f"   Analysis completed in {processing_time:.2f} seconds")
        print(f"   Response preview: {preview[:200]}...")
    
    def print_script(self, final_script):
        """Print the final video script"""
        if not self.enabled:
            return
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
    
    def print_keyword_extraction(self, keyword_extraction):
        """Print keyword extraction results"""
        if not self.enabled:
            return
        print("\n" + "="*80)
        print("🏷️ KEYWORD EXTRACTION RESULTS")
        print("="*80)
        
        for timestamp_keyword in keyword_extraction.timestamp_keywords:
            print(f"\n⏰ TIMESTAMP: {timestamp_keyword.timestamp}")
            print(f"📝 CONTENT: {timestamp_keyword.content_line}")
            print(f"🎯 KEYWORDS: {', '.join(timestamp_keyword.keywords)}")
            print("-" * 60)
        
        print("="*80)
    
    def print_search_results(self, content_search_results):
        """Print YouTube search results"""
        if not self.enabled:
            return
        print("\n" + "="*80)
        print("🔍 YOUTUBE CONTENT SEARCH RESULTS")
        print("="*80)
        
        for search_result in content_search_results.search_results:
            print(f"\n⏰ TIMESTAMP: {search_result.timestamp}")
            print(f"🎯 KEYWORDS: {', '.join(search_result.keywords)}")
            print(f"🔍 SEARCH QUERY: {search_result.search_query}")
            print(f"📄 TITLE: {search_result.title}")
            print(f"🔗 YOUTUBE LINKS:")
            if search_result.links:
                for i, link in enumerate(search_result.links, 1):
                    print(f"     {i}. {link}")
            else:
                print("     No links found")
            print("-" * 60)
        
        print("="*80)
    
    def print_video_understanding(self, video_understanding_results):
        """Print video understanding results"""
        if not self.enabled:
            return
        print("\n" + "="*80)
        print("🎥 VIDEO UNDERSTANDING RESULTS")
        print("="*80)
        
        for understanding_result in video_understanding_results.understanding_results:
            print(f"\n⏰ TIMESTAMP: {understanding_result.timestamp}")
            print(f"🎯 KEYWORDS: {', '.join(understanding_result.keywords)}")
            print(f"🔗 YOUTUBE URL: {understanding_result.youtube_url}")
            print(f"❓ ANALYSIS QUERY: {understanding_result.analysis_query}")
            print(f"⏱️ PROCESSING TIME: {understanding_result.processing_time:.2f}s")
            print(f"📊 ANALYSIS RESULT:")
            print(f"   {understanding_result.analysis_result}")
            print("-" * 60)
        
        print("="*80)
    
    def print_final_structure(self, final_video_structure):
        """Print the final video structure with raw JSON"""
        if not self.enabled:
            return
        print("\n" + "="*80)
        print("📋 FINAL VIDEO STRUCTURE")
        print("="*80)
        
        # Print raw JSON
        final_structure_dict = final_video_structure.model_dump()
        print("🔧 RAW JSON:")
        print(json.dumps(final_structure_dict, indent=2, ensure_ascii=False))
        print("="*80)
        
        # print(f"Title: {final_video_structure.title}")
        # print(f"Goal: {final_video_structure.goal}")
        # print(f"Style: {', '.join(final_video_structure.style)}")
        # print(f"Segments: {len(final_video_structure.segments)}")
        # for i, segment in enumerate(final_video_structure.segments):
        #     print(f"  Segment {i+1}:")
        #     print(f"    Time Range: {segment.time_range}")
        #     print(f"    Title: {segment.title}")
        #     print(f"    Audio: {segment.audio}")
        #     print(f"    Visual Elements: {len(segment.visual)}")
        #     for j, visual_element in enumerate(segment.visual):
        #         print(f"      Visual Element {j+1}:")
        #         print(f"        Sub Time Range: {visual_element.sub_time_range}")
        #         print(f"        Type: {visual_element.type}")
        #         if visual_element.source:
        #             print(f"        Source: {visual_element.source}")
        #         print(f"        Description: {visual_element.description}")
        #     print("-" * 40)
        print("="*80)
    
    def print_completion(self, node_name: str, count: int = None, item_type: str = "items"):
        """Print when a node completes"""
        if not self.enabled:
            return
        if count is not None:
            print(f"✅ {node_name.replace('_', ' ').title()} completed for {count} {item_type}")
        else:
            print(f"✅ {node_name.replace('_', ' ').title()} completed successfully")
        print()
    
    def print_warning(self, message: str):
        """Print warning messages"""
        if not self.enabled:
            return
        print(f"⚠️ {message}")
    
    def print_error(self, message: str):
        """Print error messages"""
        if not self.enabled:
            return
        print(f"❌ {message}")

# Global debug instance
debug = DebugPrinter(enabled=True)  # Set to False to disable all debug prints 