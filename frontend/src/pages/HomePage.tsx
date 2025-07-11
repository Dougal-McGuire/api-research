import React, { useState, useEffect } from 'react'
import { Search, FileText, AlertCircle, CheckCircle, Loader, Settings, ChevronRight, ChevronLeft, Download, Archive } from 'lucide-react'
import axios from 'axios'

interface SearchResult {
  status: string
  substance?: string
  research_content?: string
  prompt_used?: string
  model_used?: string
  message?: string
  debug_info?: any
  api_slug?: string
  pdf_summary_url?: string
  download_all_url?: string
  downloaded_files?: Array<{
    title: string
    filename: string
    source: string
    download_date: string
    local_path: string
  }>
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
  const [debugMode, setDebugMode] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [availableModels, setAvailableModels] = useState<Model[]>([])
  const [selectedModel, setSelectedModel] = useState(() => {
    // Get saved model from localStorage or default to o1
    return localStorage.getItem('selectedModel') || 'o1'
  })
  const [modelsLoading, setModelsLoading] = useState(true)
  const [rawOutput, setRawOutput] = useState(() => {
    // Get saved raw output preference from localStorage
    return localStorage.getItem('rawOutput') === 'true'
  })

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

  // Save raw output preference to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('rawOutput', rawOutput.toString())
  }, [rawOutput])

  const convertContentToHTML = (text: string): React.ReactNode => {
    if (!text) return null;
    
    // First, remove web.run citations and [web reference] markers
    let cleanedText = text;
    
    // Remove web.run citations like: Citation: web.run("url")
    cleanedText = cleanedText.replace(/Citation:\s*web\.run\([^)]+\)/g, '');
    
    // Remove [web reference #X] markers
    cleanedText = cleanedText.replace(/\[web reference #\d+\]/g, '');
    
    // Remove web.run references in text like [web.run#4]
    cleanedText = cleanedText.replace(/\[web\.run#\d+\]/g, '');
    
    // Split by lines to preserve formatting
    const lines = cleanedText.split('\n');
    
    // Process lines to identify and handle tables
    const processedLines = [];
    let inTable = false;
    let tableRows = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Check if this is a table line (contains |)
      if (line.includes('|') && line.trim().startsWith('|')) {
        if (!inTable) {
          inTable = true;
          tableRows = [];
        }
        tableRows.push(line);
      } else {
        // If we were in a table, process it
        if (inTable) {
          processedLines.push({ type: 'table', content: tableRows });
          tableRows = [];
          inTable = false;
        }
        
        // Add the current line
        if (line.trim() !== '' || (i > 0 && lines[i - 1].trim() !== '')) {
          processedLines.push({ type: 'line', content: line });
        }
      }
    }
    
    // Handle any remaining table
    if (inTable && tableRows.length > 0) {
      processedLines.push({ type: 'table', content: tableRows });
    }
    
    return processedLines.map((item, itemIndex) => {
      if (item.type === 'table') {
        return renderTable(item.content as string[], itemIndex);
      }
      
      const line = item.content as string;
      const lineIndex = itemIndex;
      
      // Check if line contains URLs
      const urlRegex = /(https?:\/\/[^\s\n\r\t<>()]+)/g;
      const parts = line.split(urlRegex);
      
      const processedLine = parts.map((part: string, partIndex: number) => {
        if (part.match(urlRegex)) {
          // Clean URL more thoroughly
          let cleanUrl = part;
          // Remove trailing punctuation and brackets
          cleanUrl = cleanUrl.replace(/[.,;:!?)]+$/, '');
          // Remove any remaining parentheses at the end
          cleanUrl = cleanUrl.replace(/\)+$/, '');
          
          return (
            <a
              key={`${lineIndex}-${partIndex}`}
              href={cleanUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline break-words"
            >
              {cleanUrl}
            </a>
          );
        }
        
        // Convert markdown-style formatting
        let processedPart = part;
        
        // Bold text
        processedPart = processedPart.replace(/\*\*([^*]+)\*\*/g, (_match: string, p1: string) => {
          return `<strong class="font-semibold">${p1}</strong>`;
        });
        
        // Italic text
        processedPart = processedPart.replace(/\*([^*]+)\*/g, (_match: string, p1: string) => {
          return `<em class="italic">${p1}</em>`;
        });
        
        return (
          <span 
            key={`${lineIndex}-${partIndex}`}
            dangerouslySetInnerHTML={{ __html: processedPart }}
          />
        );
      });
      
      // Handle different line types
      if (line.trim().startsWith('•') || line.trim().startsWith('–')) {
        // Remove duplicate bullet points that might appear
        const cleanLine = line.replace(/^[\s]*[•–]+[\s]*[•–]+[\s]*/, '• ');
        const cleanProcessedLine = cleanLine.split(urlRegex).map((part: string, partIndex: number) => {
          if (part.match(urlRegex)) {
            let cleanUrl = part.replace(/[.,;:!?)]+$/, '').replace(/\)+$/, '');
            return (
              <a
                key={`${lineIndex}-${partIndex}`}
                href={cleanUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline break-words"
              >
                {cleanUrl}
              </a>
            );
          }
          let processedPart = part;
          processedPart = processedPart.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold">$1</strong>');
          processedPart = processedPart.replace(/\*([^*]+)\*/g, '<em class="italic">$1</em>');
          return (
            <span 
              key={`${lineIndex}-${partIndex}`}
              dangerouslySetInnerHTML={{ __html: processedPart }}
            />
          );
        });
        
        return (
          <li key={lineIndex} className="ml-6 mb-1 list-disc">
            {cleanProcessedLine}
          </li>
        );
      } else if (line.trim().match(/^\d+\./)) {
        return (
          <div key={lineIndex} className="mb-2 ml-2">
            {processedLine}
          </div>
        );
      } else if (line.trim() === '') {
        return <br key={lineIndex} />;
      } else if (line.trim().match(/^#{1,6}\s/)) {
        // Handle markdown headers
        const headerLevel = line.match(/^(#{1,6})\s/)?.[1]?.length || 1;
        const headerText = line.replace(/^#{1,6}\s/, '');
        const HeaderTag = `h${Math.min(headerLevel + 1, 6)}` as any;
        return (
          <HeaderTag key={lineIndex} className={`font-semibold mt-4 mb-2 text-${7 - headerLevel}xl`}>
            {headerText}
          </HeaderTag>
        );
      } else {
        return (
          <div key={lineIndex} className="mb-1">
            {processedLine}
          </div>
        );
      }
    }).filter(Boolean); // Remove null entries
  };

  const renderTable = (tableLines: string[], key: number) => {
    if (tableLines.length === 0) return null;
    
    // Filter out separator lines (lines with only | - and spaces)
    const contentLines = tableLines.filter(line => !line.match(/^\s*\|[\s\-\|]*\|\s*$/));
    
    if (contentLines.length === 0) return null;
    
    const [headerLine, ...bodyLines] = contentLines;
    
    // Parse header
    const headers = headerLine.split('|').map(cell => cell.trim()).filter(cell => cell !== '');
    
    // Parse body rows
    const rows = bodyLines.map(line => 
      line.split('|').map(cell => cell.trim()).filter(cell => cell !== '')
    );
    
    return (
      <div key={key} className="my-4 overflow-x-auto">
        <table className="min-w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-50">
              {headers.map((header, index) => (
                <th key={index} className="border border-gray-300 px-4 py-2 text-left font-semibold">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex} className="border border-gray-300 px-4 py-2">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

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

    // Show dynamic status messages during research
    {
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
    }
  }


  return (
    <div className="py-12 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
            Clinical Research Helper
          </h1>
          <p className="mt-3 max-w-2xl mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl">
            AI-powered search across EMA EPAR, EMA-PSBG, FDA Approvals, and FDA-PSBG databases for comprehensive pharmaceutical regulatory intelligence
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
              AI-powered comprehensive search across four mandatory regulatory sources: EMA EPAR (European Public Assessment Reports), EMA-PSBG (Product-Specific Bioequivalence Guidance), FDA Approvals (Drugs@FDA), and FDA-PSBG (Product-Specific Guidance).
            </p>
          </div>
        </div>

        {/* Dynamic Status Message */}
        {isLoading && statusMessage && (
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
            <div className="bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-xs overflow-auto max-h-96">
              <h3 className="text-white font-semibold mb-3">🐛 Debug Information</h3>
              <pre className="whitespace-pre-wrap">{JSON.stringify(searchResult.debug_info, null, 2)}</pre>
            </div>
          </div>
        )}

        {/* Search Results */}
        {searchResult && (
          <div className="mt-12 max-w-6xl mx-auto">
            {(searchResult.status === 'completed' || searchResult.research_content) ? (
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
                {searchResult.research_content && (
                  <div className="mt-6">
                    <div className="bg-white border border-gray-200 rounded-lg p-6 overflow-hidden">
                      <div className="max-h-[600px] overflow-y-auto">
                        {rawOutput ? (
                          <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                            {searchResult.research_content}
                          </pre>
                        ) : (
                          <div className="prose prose-sm max-w-none">
                            {convertContentToHTML(searchResult.research_content)}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

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

          {/* Raw Output Toggle */}
          <div className="mb-6">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="sidebar-raw-output"
                checked={rawOutput}
                onChange={(e) => setRawOutput(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="sidebar-raw-output" className="text-sm text-gray-700">
                Raw LLM Output
              </label>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Display unprocessed AI response without parsing or formatting
            </p>
          </div>

          {/* Download Section */}
          {searchResult && searchResult.status === 'completed' && (
            <div className="mb-6 border-t border-gray-200 pt-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Downloads</h3>
              
              {/* Download PDF Summary */}
              {searchResult.pdf_summary_url && (
                <div className="mb-3">
                  <a
                    href={searchResult.pdf_summary_url}
                    download
                    className="w-full flex items-center justify-between px-3 py-2 text-sm bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Download className="h-4 w-4 text-blue-600" />
                      <span className="text-blue-700">Summary Report (PDF)</span>
                    </div>
                  </a>
                </div>
              )}

              {/* Download All Documents */}
              {searchResult.download_all_url && (
                <div className="mb-3">
                  <a
                    href={searchResult.download_all_url}
                    className="w-full flex items-center justify-between px-3 py-2 text-sm bg-green-50 border border-green-200 rounded-md hover:bg-green-100 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Archive className="h-4 w-4 text-green-600" />
                      <span className="text-green-700">All Documents (ZIP)</span>
                    </div>
                  </a>
                </div>
              )}

              {/* Downloaded Files List */}
              {searchResult.downloaded_files && searchResult.downloaded_files.length > 0 && (
                <div>
                  <p className="text-xs text-gray-500 mb-2">
                    Downloaded {searchResult.downloaded_files.length} documents
                  </p>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {searchResult.downloaded_files.map((file, index) => (
                      <div key={index} className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                        <div className="font-medium">{file.source}</div>
                        <div className="text-gray-500">{file.download_date}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
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