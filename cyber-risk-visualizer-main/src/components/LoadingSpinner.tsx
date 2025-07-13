
import React from 'react';
import { Shield } from 'lucide-react';

const LoadingSpinner = () => {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="relative mb-8">
          <div className="w-16 h-16 border-4 border-red-600 border-opacity-20 rounded-full animate-spin"></div>
          <div className="absolute inset-0 w-16 h-16 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
          <div className="absolute inset-4 w-8 h-8 bg-red-600 rounded-full flex items-center justify-center">
            <Shield className="w-4 h-4 text-white" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">AI Security Analysis</h2>
        <p className="text-gray-400 mb-4">Scanning network and analyzing vulnerabilities...</p>
        <div className="flex items-center justify-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
            <span className="text-red-400 text-sm">LLM Engine</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-red-500 text-sm">CVE Analysis</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-300 rounded-full animate-pulse"></div>
            <span className="text-red-300 text-sm">Patch Discovery</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
