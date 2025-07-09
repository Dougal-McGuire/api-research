import React from 'react'
import { Link } from 'react-router-dom'
import { Home } from 'lucide-react'

const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <Link to="/" className="flex items-center space-x-3">
            <Home className="h-8 w-8 text-primary-600" />
            <span className="text-2xl font-bold text-gray-900">api-research</span>
          </Link>
        </div>
      </div>
    </header>
  )
}

export default Header