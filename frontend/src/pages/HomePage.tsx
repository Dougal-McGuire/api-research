import React, { useState, useEffect } from 'react'
import { Search, Download, FileText, AlertCircle, CheckCircle, Loader, Settings, ChevronRight, ChevronLeft } from 'lucide-react'
import axios from 'axios'

interface FileInfo {
  source: string
  title: string
  filename: string
  url: string
  original_url: string
  size_bytes: number
}

interface SearchResult {
  status: string
  substance?: string
  research_content?: string
  prompt_used?: string
  model_used?: string
  message?: string
  debug_info?: any
}

interface Model {
  id: string
  name: string
  description: string
}

const HomePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [debugMode, setDebugMode] = useState(true)
  const [statusMessage, setStatusMessage] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [availableModels, setAvailableModels] = useState<Model[]>([])
  const [selectedModel, setSelectedModel] = useState(() => {
    // Get saved model from localStorage or default to o1
    return localStorage.getItem('selectedModel') || 'o1'
  })
  const [modelsLoading, setModelsLoading] = useState(true)

  // Fetch available models on component mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get('/api/research/models')
        setAvailableModels(response.data.models)
      } catch (err) {
        console.error('Failed to fetch models:', err)
        // Fallback to hardcoded models if API fails
        setAvailableModels([
          { id: 'o1', name: 'o1', description: 'Latest Reasoning + Web Search' },
          { id: 'o1-mini', name: 'o1-mini', description: 'Reasoning + Web Search' },
          { id: 'o3-mini', name: 'o3-mini', description: 'Next-Gen Reasoning + Web Search' }
        ])
      } finally {
        setModelsLoading(false)
      }
    }
    fetchModels()
  }, [])

  // Save selected model to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('selectedModel', selectedModel)
  }, [selectedModel])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!searchQuery.trim()) {
      setError('Please enter a pharmaceutical API name')
      return
    }

    setIsLoading(true)
    setError(null)
    setSearchResult(null)
    setStatusMessage('')

    // Show dynamic status messages if debug mode is enabled
    if (debugMode) {
      const statusMessages = [
        'Initializing OpenAI research session...',
        'Loading research prompt template...',
        'Formatting search query for regulatory databases...',
        'Calling OpenAI o1 model for deep research...',
        'Analyzing EMA EPAR database...',
        'Searching FDA approval records...',
        'Reviewing regulatory documents...',
        'Extracting key information and references...',
        'Formatting comprehensive research report...',
        'Finalizing results with clickable links...'
      ]

      let messageIndex = 0
      const statusInterval = setInterval(() => {
        if (messageIndex < statusMessages.length) {
          setStatusMessage(statusMessages[messageIndex])
          messageIndex++
        } else {
          // Loop back to create continuous scrolling effect
          messageIndex = 0
        }
      }, 2000) // Change message every 2 seconds

      try {
        const response = await axios.post('/api/research/search', {
          api_name: searchQuery.trim(),
          debug: debugMode,
          model: selectedModel
        })
        
        clearInterval(statusInterval)
        setStatusMessage('Research completed successfully!')
        setSearchResult(response.data)
      } catch (err: any) {
        clearInterval(statusInterval)
        setStatusMessage('')
        setError(err.response?.data?.detail || 'Search failed. Please try again.')
      } finally {
        setIsLoading(false)
        setTimeout(() => setStatusMessage(''), 2000) // Clear success message after 2 seconds
      }
    } else {
      // Non-debug mode - simple request
      try {
        const response = await axios.post('/api/research/search', {
          api_name: searchQuery.trim(),
          debug: debugMode,
          model: selectedModel
        })
        
        setSearchResult(response.data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Search failed. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const convertUrlsToLinks = (text: string): React.ReactNode => {
    // Regular expression to match URLs
    const urlRegex = /(https?:\/\/[^\s\n\r\t]+)/g;
    const parts = text.split(urlRegex);
    
    return parts.map((part, index) => {
      if (part.match(urlRegex)) {
        return (
          <a
            key={index}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline break-all"
          >
            {part}
          </a>
        );
      }
      return part;
    });
  }

  return (
    <div className="py-12 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
            Clinical Research Helper
          </h1>
          <p className="mt-3 max-w-2xl mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl">
            Search and download regulatory documents for pharmaceutical active ingredients from major health authorities
          </p>
        </div>
        
        {/* Search Form */}
        <div className="mt-16 max-w-2xl mx-auto">
          <form onSubmit={handleSearch} className="relative">
            <div className="flex">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter pharmaceutical API name (e.g., ibuprofen, dexamethasone)"
                className="input-field flex-1 pr-24"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !searchQuery.trim()}
                className="btn-primary ml-4 flex items-center space-x-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader className="h-5 w-5 animate-spin" />
                ) : (
                  <Search className="h-5 w-5" />
                )}
                <span>{isLoading ? 'Searching...' : 'Search'}</span>
              </button>
            </div>
          </form>
          
          {/* Search Info */}
          <div className="mt-4 text-sm text-gray-600">
            <p>
              We search regulatory documents from EMA, FDA, NICE, and Health Canada.
              The AI system will automatically filter for relevant approval and assessment documents.
            </p>
            
            {/* Debug Toggle */}
            <div className="mt-3 flex items-center space-x-2">
              <input
                type="checkbox"
                id="debug-mode"
                checked={debugMode}
                onChange={(e) => setDebugMode(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="debug-mode" className="text-sm text-gray-600">
                Enable debug mode (show detailed search information)
              </label>
            </div>
          </div>
        </div>

        {/* Dynamic Status Message (Debug Mode) */}
        {debugMode && isLoading && statusMessage && (
          <div className="mt-8 max-w-2xl mx-auto">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center space-x-3">
              <Loader className="h-5 w-5 text-blue-500 animate-spin" />
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-800">Research Progress</p>
                <p className="mt-1 text-sm text-blue-700">{statusMessage}</p>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-8 max-w-2xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Search Error</h3>
                <p className="mt-1 text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Debug Information */}
        {debugMode && searchResult?.debug_info && (
          <div className="mt-8 max-w-4xl mx-auto">
            <div className="bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-sm">
              <h3 className="text-white font-semibold mb-3">🐛 Debug Information</h3>
              <div className="space-y-2">
                <div><span className="text-gray-400">Substance searched:</span> {searchResult.debug_info.substance_searched}</div>
                <div><span className="text-gray-400">Model used:</span> {searchResult.model_used}</div>
                <div><span className="text-gray-400">Template file:</span> {searchResult.debug_info.template_file}</div>
                <div><span className="text-gray-400">Template length:</span> {searchResult.debug_info.template_length} characters</div>
                <div><span className="text-gray-400">Formatted prompt length:</span> {searchResult.debug_info.formatted_prompt_length} characters</div>
                <div><span className="text-gray-400">Response length:</span> {searchResult.debug_info.response_length} characters</div>
                
                {searchResult.debug_info.actual_prompt_used && (
                  <div className="mt-3">
                    <span className="text-gray-400">Actual prompt used:</span>
                    <div className="ml-4 mt-1 p-2 bg-gray-800 rounded text-xs max-h-60 overflow-y-auto">
                      <pre className="whitespace-pre-wrap">{searchResult.debug_info.actual_prompt_used}</pre>
                    </div>
                  </div>
                )}
                
                {searchResult.debug_info.error && (
                  <div className="mt-3 text-red-400">
                    <span className="text-gray-400">Error:</span> {searchResult.debug_info.error}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Search Results */}
        {searchResult && (
          <div className="mt-12 max-w-6xl mx-auto">
            {searchResult.status === 'completed' && searchResult.research_content ? (
              <div className="card">
                <div className="flex items-center space-x-3 mb-6">
                  <CheckCircle className="h-6 w-6 text-green-500" />
                  <div>
                    <h2 className="text-2xl font-semibold text-gray-900">
                      Research Results for "{searchResult.substance}"
                    </h2>
                    <p className="text-gray-600">
                      Generated using {searchResult.model_used} with web search capabilities
                    </p>
                  </div>
                </div>

                {/* Research Content */}
                <div className="prose prose-lg max-w-none">
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                      {convertUrlsToLinks(searchResult.research_content)}
                    </div>
                  </div>
                </div>

                {/* Copy to Clipboard Button */}
                <div className="mt-6 flex justify-end">
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(searchResult.research_content || '')
                      // You could add a toast notification here
                    }}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <FileText className="h-5 w-5" />
                    <span>Copy Research to Clipboard</span>
                  </button>
                </div>
              </div>
            ) : searchResult.status === 'error' ? (
              <div className="card text-center">
                <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Research Failed
                </h2>
                <p className="text-gray-600">
                  {searchResult.message || 'The research request failed. Please try again.'}
                </p>
              </div>
            ) : (
              <div className="card text-center">
                <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  No Research Results
                </h2>
                <p className="text-gray-600">
                  {searchResult.message || 'No research content was generated. Please try a different search term.'}
                </p>
              </div>
            )}
          </div>
        )}

      </div>

      {/* Sidebar Toggle Button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="fixed top-1/2 right-4 z-50 bg-primary-600 text-white p-2 rounded-l-lg shadow-lg hover:bg-primary-700 transition-colors"
      >
        {sidebarOpen ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
      </button>

      {/* Collapsible Sidebar */}
      <div className={`fixed top-0 right-0 h-full w-80 bg-white shadow-2xl transform transition-transform duration-300 ease-in-out z-40 ${
        sidebarOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>Settings & Tools</span>
            </h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>

          {/* Model Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Model
            </label>
            {modelsLoading ? (
              <div className="flex items-center justify-center py-3">
                <Loader className="h-5 w-5 animate-spin text-primary-600" />
                <span className="ml-2 text-sm text-gray-600">Loading models...</span>
              </div>
            ) : (
              <>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  {availableModels.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.name} {model.description && `(${model.description})`}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  Select the AI model for research. o1/o3 models provide deeper reasoning but take longer.
                </p>
              </>
            )}
          </div>

          {/* Debug Mode Toggle */}
          <div className="mb-6">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="sidebar-debug-mode"
                checked={debugMode}
                onChange={(e) => setDebugMode(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="sidebar-debug-mode" className="text-sm text-gray-700">
                Debug Mode
              </label>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Show detailed search information and progress updates
            </p>
          </div>
        </div>
      </div>

      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default HomePage