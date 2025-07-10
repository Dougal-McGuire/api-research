import React from 'react'
import { Link } from 'react-router-dom'
import { FileSearch } from 'lucide-react'

const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <Link to="/" className="flex items-center space-x-3">
            <FileSearch className="h-8 w-8 text-primary-600" />
            <span className="text-2xl font-bold text-gray-900">Clinical Research Helper</span>
          </Link>
          <nav className="flex items-center space-x-6">
            <a 
              href="/api/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-gray-900 font-medium"
            >
              API Docs
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header