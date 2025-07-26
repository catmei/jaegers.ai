"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import {
  Loader2,
  Copy,
  Download,
  FileText,
  ChevronDown,
  ChevronUp,
  Maximize2,
  Play,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react"

// Define types for the video data structure
type VideoSource = {
  platform?: string
  url?: string
  time_range?: string
} | string | null

type Visual = {
  sub_time_range: string
  type: string
  source: VideoSource
  description: string
}

type Segment = {
  time_range: string
  title: string
  visual: Visual[]
  audio: string
}

type VideoData = {
  title: string
  goal: string
  style: string[]
  segments: Segment[]
}

export default function HomePage() {
  const [topic, setTopic] = useState<string>("")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [videoData, setVideoData] = useState<VideoData | null>(null)
  const [collapsedConcepts, setCollapsedConcepts] = useState<Set<string>>(new Set())
  const [canScrollLeft, setCanScrollLeft] = useState<boolean>(false)
  const [canScrollRight, setCanScrollRight] = useState<boolean>(false)
  const [focusedSegment, setFocusedSegment] = useState<number | null>(null)
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  const handleGenerate = async () => {
    if (!topic.trim()) return

    setIsLoading(true)

    try {
      // Fetch mock data from public folder
      const response = await fetch('/mockData.json')
      const data = await response.json()
      
      setTimeout(() => {
        setVideoData(data)
        setIsLoading(false)
        // Collapse all concept segments by default
        const conceptIndices = new Set<string>()
        data.segments.forEach((segment: Segment, segmentIndex: number) => {
          segment.visual.forEach((visual, visualIndex) => {
            if (visual.type === "concept") {
              conceptIndices.add(`${segmentIndex}-${visualIndex}`)
            }
          })
        })
        setCollapsedConcepts(conceptIndices)
      }, 2000)
    } catch (error) {
      console.error('Error loading mock data:', error)
      setIsLoading(false)
    }
  }

  const checkScrollButtons = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current
      setCanScrollLeft(scrollLeft > 0)
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1)
    }
  }

  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: -400, behavior: "smooth" })
    }
  }

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: 400, behavior: "smooth" })
    }
  }

  const handleSegmentClick = (segmentIndex: number) => {
    setFocusedSegment(segmentIndex === focusedSegment ? null : segmentIndex)
  }

  const closeFocusMode = () => {
    setFocusedSegment(null)
  }

  useEffect(() => {
    if (videoData) {
      checkScrollButtons()
      const container = scrollContainerRef.current
      if (container) {
        container.addEventListener("scroll", checkScrollButtons)
        window.addEventListener("resize", checkScrollButtons)
        return () => {
          container.removeEventListener("scroll", checkScrollButtons)
          window.removeEventListener("resize", checkScrollButtons)
        }
      }
    }
  }, [videoData])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const toggleConcept = (segmentIndex: number, visualIndex: number) => {
    const key = `${segmentIndex}-${visualIndex}`
    const newCollapsed = new Set(collapsedConcepts)
    if (newCollapsed.has(key)) {
      newCollapsed.delete(key)
    } else {
      newCollapsed.add(key)
    }
    setCollapsedConcepts(newCollapsed)
  }

  const getYouTubeVideoId = (url: string): string | null => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)
    return match ? match[1] : null
  }

  const parseTimeToSeconds = (timeStr: string): number => {
    const parts = timeStr.split(":")
    if (parts.length === 3) {
      return Number.parseInt(parts[0]) * 3600 + Number.parseInt(parts[1]) * 60 + Number.parseInt(parts[2])
    } else if (parts.length === 2) {
      return Number.parseInt(parts[0]) * 60 + Number.parseInt(parts[1])
    }
    return 0
  }

  const getYouTubeEmbedUrl = (url: string, timeRange?: string): string | null => {
    const videoId = getYouTubeVideoId(url)
    if (!videoId) return null

    let startSeconds = 0
    if (timeRange) {
      const startTimeStr = timeRange.split(" - ")[0] || timeRange
      startSeconds = parseTimeToSeconds(startTimeStr)
    }

    return `https://www.youtube.com/embed/${videoId}?start=${startSeconds}&autoplay=0&rel=0`
  }

  const getYouTubeThumbnail = (url: string): string => {
    const videoId = getYouTubeVideoId(url)
    return videoId ? `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg` : "/placeholder.svg?height=180&width=320"
  }

  const getVideoUrl = (source: VideoSource): string | null => {
    if (typeof source === 'string') {
      return source
    }
    if (source && typeof source === 'object' && 'url' in source) {
      return source.url || null
    }
    return null
  }

  const getTotalDuration = (): number => {
    if (!videoData?.segments?.length) return 60 // Default 60 seconds
    const lastSegment = videoData.segments[videoData.segments.length - 1]
    const endTime = lastSegment.time_range.split("-")[1]
    const parts = endTime.split(":")
    return Number.parseInt(parts[0]) * 60 + Number.parseInt(parts[1])
  }

  const getSegmentDuration = (timeRange: string): number => {
    const [start, end] = timeRange.split("-")
    const startParts = start.split(":")
    const endParts = end.split(":")
    const startSeconds = Number.parseInt(startParts[0]) * 60 + Number.parseInt(startParts[1])
    const endSeconds = Number.parseInt(endParts[0]) * 60 + Number.parseInt(endParts[1])
    return endSeconds - startSeconds
  }

  const getSegmentWidth = (timeRange: string): number => {
    const duration = getSegmentDuration(timeRange)
    const totalDuration = getTotalDuration()
    return Math.max((duration / totalDuration) * 100, 5) // Minimum 5% width
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-indigo-600" />
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">Hunting for clips...</h2>
          <p className="text-gray-600">Creating your video storyboard</p>
        </div>
      </div>
    )
  }

  if (videoData) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-gray-900 mb-1">{videoData.title}</h1>
                <p className="text-gray-600 text-sm mb-2">{videoData.goal}</p>
                <div className="flex flex-wrap gap-2">
                  {videoData.style.map((style, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {style}
                    </Badge>
                  ))}
                </div>
              </div>
              <div className="flex gap-2 ml-4">
                <Button variant="outline" size="sm" className="flex items-center gap-1 bg-transparent">
                  <Download className="h-3 w-3" />
                  CSV
                </Button>
                <Button variant="outline" size="sm" className="flex items-center gap-1 bg-transparent">
                  <FileText className="h-3 w-3" />
                  Script
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setVideoData(null)
                    setTopic("")
                    setFocusedSegment(null)
                  }}
                >
                  New Plan
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Focus Mode Overlay */}
        {focusedSegment !== null && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden relative">
              {/* Focus Mode Header - Fixed */}
              <div className="bg-white border-b p-4 pr-16 rounded-t-xl relative z-10">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{videoData.segments[focusedSegment].title}</h2>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="font-mono text-sm">
                      {videoData.segments[focusedSegment].time_range}
                    </Badge>
                    <Badge variant="secondary" className="text-sm">
                      {getSegmentDuration(videoData.segments[focusedSegment].time_range)}s
                    </Badge>
                  </div>
                </div>
                {/* Close button positioned absolutely */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={closeFocusMode}
                  className="absolute top-4 right-4 h-8 w-8 p-0 bg-white hover:bg-gray-50 border-gray-300 z-20"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Focus Mode Content - Scrollable */}
              <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
                <div className="p-6 space-y-6">
                  {videoData.segments[focusedSegment].visual.map((visual, visualIndex) => {
                    const isCollapsed = collapsedConcepts.has(`${focusedSegment}-${visualIndex}`)
                    const videoUrl = getVideoUrl(visual.source)

                    if (visual.type === "clip" && videoUrl) {
                      return (
                        <div key={visualIndex} className="border-2 border-red-200 rounded-lg overflow-hidden bg-red-50">
                          <div className="p-4 bg-red-100 border-b border-red-200">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <Play className="h-5 w-5 text-red-600" />
                                <Badge variant="destructive" className="text-sm">
                                  YouTube Clip
                                </Badge>
                              </div>
                              <Badge variant="outline" className="font-mono text-sm">
                                {visual.sub_time_range}
                              </Badge>
                            </div>
                            {typeof visual.source === 'object' && visual.source?.time_range && (
                              <Badge variant="outline" className="font-mono text-sm bg-white">
                                {visual.source.time_range}
                              </Badge>
                            )}
                          </div>

                          <div className="p-4">
                            {/* Larger YouTube Embed for Focus Mode */}
                            <div className="relative mb-4">
                              <iframe
                                src={getYouTubeEmbedUrl(videoUrl, typeof visual.source === 'object' ? visual.source?.time_range : undefined) || ''}
                                className="w-full h-80 rounded-lg"
                                frameBorder="0"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                              />
                              <div className="absolute top-2 right-2">
                                <Button
                                  size="sm"
                                  variant="secondary"
                                  className="h-8 w-8 p-0 bg-black/50 hover:bg-black/70 text-white border-0"
                                  onClick={() => window.open(videoUrl, "_blank")}
                                >
                                  <Maximize2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>

                            <p className="text-base text-gray-700 mb-4">{visual.description}</p>

                            <Button
                              size="default"
                              variant="outline"
                              onClick={() => copyToClipboard(videoUrl)}
                              className="w-full"
                            >
                              <Copy className="h-4 w-4 mr-2" />
                              Copy YouTube Link
                            </Button>
                          </div>
                        </div>
                      )
                    } else {
                      return (
                        <div key={visualIndex} className="border border-gray-200 rounded-lg overflow-hidden">
                          <Collapsible
                            open={!isCollapsed}
                            onOpenChange={() => toggleConcept(focusedSegment, visualIndex)}
                          >
                            <CollapsibleTrigger asChild>
                              <div className="p-4 bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 bg-gray-400 rounded-full" />
                                    <Badge variant="outline" className="text-sm">
                                      Concept
                                    </Badge>
                                    <Badge variant="outline" className="font-mono text-sm">
                                      {visual.sub_time_range}
                                    </Badge>
                                  </div>
                                  {isCollapsed ? (
                                    <ChevronDown className="h-5 w-5 text-gray-500" />
                                  ) : (
                                    <ChevronUp className="h-5 w-5 text-gray-500" />
                                  )}
                                </div>
                                {isCollapsed && <p className="text-sm text-gray-600 mt-2">{visual.description}</p>}
                              </div>
                            </CollapsibleTrigger>

                            <CollapsibleContent>
                              <div className="p-4 border-t border-gray-200">
                                <p className="text-sm text-gray-700">{visual.description}</p>
                              </div>
                            </CollapsibleContent>
                          </Collapsible>
                        </div>
                      )
                    }
                  })}

                  {/* Audio Direction in Focus Mode */}
                  {videoData.segments[focusedSegment].audio && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-3 h-3 bg-blue-500 rounded-full" />
                        <h4 className="text-sm font-medium text-blue-900">Audio Direction</h4>
                      </div>
                      <p className="text-base text-blue-800">{videoData.segments[focusedSegment].audio}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1 p-4 pt-16">
          <div className="max-w-7xl mx-auto">
            <div className="relative">
              <div
                ref={scrollContainerRef}
                className="overflow-x-auto pb-4 scrollbar-hide"
                onScroll={checkScrollButtons}
              >
                <div className="flex gap-4 min-w-max">
                  {videoData.segments.map((segment, segmentIndex) => (
                    <div
                      key={segmentIndex}
                      className={`flex-shrink-0 bg-white rounded-lg shadow-sm border cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-[1.02] hover:border-indigo-300 hover:bg-gradient-to-br hover:from-white hover:to-indigo-50 hover:transform hover:origin-bottom ${
                        focusedSegment === segmentIndex ? "ring-2 ring-indigo-500 shadow-lg scale-105" : ""
                      }`}
                      style={{ minWidth: "400px", maxWidth: "500px" }}
                      onClick={() => handleSegmentClick(segmentIndex)}
                    >
                      {/* Segment Header */}
                      <div className="p-4 border-b bg-gray-50 rounded-t-lg transition-colors duration-300 hover:bg-indigo-50">
                        <h3 className="font-semibold text-gray-900 text-sm mb-2 line-clamp-2">{segment.title}</h3>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="font-mono text-xs">
                            {segment.time_range}
                          </Badge>
                          <Badge variant="secondary" className="text-xs">
                            {getSegmentDuration(segment.time_range)}s
                          </Badge>
                        </div>
                      </div>

                      {/* Visual Content */}
                      <div className="p-4 space-y-4">
                        {segment.visual.map((visual, visualIndex) => {
                          const isCollapsed = collapsedConcepts.has(`${segmentIndex}-${visualIndex}`)
                          const videoUrl = getVideoUrl(visual.source)

                          if (visual.type === "clip" && videoUrl) {
                            // YouTube clips - always prominent and expanded
                            return (
                              <div
                                key={visualIndex}
                                className="border-2 border-red-200 rounded-lg overflow-hidden bg-red-50"
                              >
                                <div className="p-3 bg-red-100 border-b border-red-200">
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                      <Play className="h-4 w-4 text-red-600" />
                                      <Badge variant="destructive" className="text-xs">
                                        YouTube Clip
                                      </Badge>
                                    </div>
                                    <Badge variant="outline" className="font-mono text-xs">
                                      {visual.sub_time_range}
                                    </Badge>
                                  </div>
                                  {typeof visual.source === 'object' && visual.source?.time_range && (
                                    <Badge variant="outline" className="font-mono text-xs bg-white">
                                      {visual.source.time_range}
                                    </Badge>
                                  )}
                                </div>

                                <div className="p-3">
                                  {/* YouTube Embed */}
                                  <div className="relative mb-3">
                                    <iframe
                                      src={getYouTubeEmbedUrl(videoUrl, typeof visual.source === 'object' ? visual.source?.time_range : undefined) || ''}
                                      className="w-full h-48 rounded-lg"
                                      frameBorder="0"
                                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                      allowFullScreen
                                    />
                                    <div className="absolute top-2 right-2">
                                      <Button
                                        size="sm"
                                        variant="secondary"
                                        className="h-8 w-8 p-0 bg-black/50 hover:bg-black/70 text-white border-0"
                                        onClick={(e) => {
                                          e.stopPropagation()
                                          window.open(videoUrl, "_blank")
                                        }}
                                      >
                                        <Maximize2 className="h-3 w-3" />
                                      </Button>
                                    </div>
                                  </div>

                                  <p className="text-sm text-gray-700 mb-3 line-clamp-3">{visual.description}</p>

                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      copyToClipboard(videoUrl)
                                    }}
                                    className="w-full"
                                  >
                                    <Copy className="h-3 w-3 mr-2" />
                                    Copy YouTube Link
                                  </Button>
                                </div>
                              </div>
                            )
                          } else {
                            // Concept content - collapsible and more compact
                            return (
                              <div key={visualIndex} className="border border-gray-200 rounded-lg overflow-hidden">
                                <Collapsible
                                  open={!isCollapsed}
                                  onOpenChange={() => toggleConcept(segmentIndex, visualIndex)}
                                >
                                  <CollapsibleTrigger asChild>
                                    <div
                                      className="p-3 bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors"
                                      onClick={(e) => e.stopPropagation()}
                                    >
                                      <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                          <div className="w-2 h-2 bg-gray-400 rounded-full" />
                                          <Badge variant="outline" className="text-xs">
                                            Concept
                                          </Badge>
                                          <Badge variant="outline" className="font-mono text-xs">
                                            {visual.sub_time_range}
                                          </Badge>
                                        </div>
                                        {isCollapsed ? (
                                          <ChevronDown className="h-4 w-4 text-gray-500" />
                                        ) : (
                                          <ChevronUp className="h-4 w-4 text-gray-500" />
                                        )}
                                      </div>
                                      {isCollapsed && (
                                        <p className="text-xs text-gray-600 mt-2 line-clamp-2">{visual.description}</p>
                                      )}
                                    </div>
                                  </CollapsibleTrigger>

                                  <CollapsibleContent>
                                    <div className="p-3 border-t border-gray-200">
                                      <p className="text-sm text-gray-700">{visual.description}</p>
                                    </div>
                                  </CollapsibleContent>
                                </Collapsible>
                              </div>
                            )
                          }
                        })}

                        {/* Audio Direction */}
                        {segment.audio && (
                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="w-2 h-2 bg-blue-500 rounded-full" />
                              <h4 className="text-xs font-medium text-blue-900">Audio Direction</h4>
                            </div>
                            <p className="text-xs text-blue-800">{segment.audio}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Enhanced Scroll Buttons */}
              {canScrollLeft && (
                <Button
                  onClick={scrollLeft}
                  className="fixed left-6 top-1/2 transform -translate-y-1/2 z-20 h-16 w-16 rounded-full bg-indigo-600 hover:bg-indigo-700 shadow-2xl border-0 p-0 transition-all duration-300"
                >
                  <ChevronLeft className="h-8 w-8 text-white" />
                </Button>
              )}

              {canScrollRight && (
                <Button
                  onClick={scrollRight}
                  className="fixed right-6 top-1/2 transform -translate-y-1/2 z-20 h-16 w-16 rounded-full bg-indigo-600 hover:bg-indigo-700 shadow-2xl border-0 p-0 transition-all duration-300"
                >
                  <ChevronRight className="h-8 w-8 text-white" />
                </Button>
              )}

              {/* Scroll Indicators */}
              {canScrollLeft && (
                <div className="absolute left-0 top-0 bottom-4 w-12 bg-gradient-to-r from-gray-50 to-transparent pointer-events-none" />
              )}
              {canScrollRight && (
                <div className="absolute right-0 top-0 bottom-4 w-12 bg-gradient-to-l from-gray-50 to-transparent pointer-events-none" />
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="max-w-2xl mx-auto px-4 text-center">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">ClipHunt Agent</h1>
          <p className="text-lg text-gray-600 mb-8">
            Transform any topic into an interactive video storyboard with YouTube clips. Just enter your topic and let
            AI hunt for the perfect clips.
          </p>

          <div className="space-y-4">
            <Input
              type="text"
              placeholder="Enter your video topic (e.g., 'The History of AI')"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="text-lg py-3 px-4"
              onKeyPress={(e) => e.key === "Enter" && handleGenerate()}
            />
            <Button
              onClick={handleGenerate}
              disabled={!topic.trim()}
              size="lg"
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-lg py-3"
            >
              Generate Video Plan
            </Button>
          </div>

          <div className="mt-8 text-sm text-gray-500">
            <p>✨ One-click magic • 🎬 Focus mode • 📺 Prominent YouTube clips</p>
          </div>
        </div>
      </div>
    </div>
  )
}
