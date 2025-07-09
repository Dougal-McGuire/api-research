import React from 'react'

const HomePage: React.FC = () => {
  return (
    <div className="py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
            Welcome to api-research
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Modern web application built with FastAPI and React
          </p>
        </div>
        
        <div className="mt-16">
          <div className="max-w-3xl mx-auto">
            <div className="card">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Ready to Start Building
              </h2>
              <p className="text-gray-600 mb-6">
                Your project is set up with a modern tech stack including FastAPI for the backend and React with TypeScript for the frontend. The development environment is ready to go!
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Backend Features</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• FastAPI with automatic OpenAPI docs</li>
                    <li>• Hot reload development server</li>
                    <li>• Docker containerization</li>
                    <li>• CORS middleware configured</li>
                  </ul>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Frontend Features</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• React 18 with TypeScript</li>
                    <li>• Vite for fast development</li>
                    <li>• Tailwind CSS for styling</li>
                    <li>• React Router for navigation</li>
                  </ul>
                </div>
              </div>
              <div className="mt-6 text-center">
                <a
                  href="/api/docs"
                  className="btn-primary mr-4"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View API Docs
                </a>
                <a
                  href="https://github.com/your-username/api-research"
                  className="text-primary-600 hover:text-primary-700 font-medium"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on GitHub
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage