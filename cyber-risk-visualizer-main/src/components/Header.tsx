
import React from 'react';
import { Shield, Globe, TrendingUp } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-gray-800 border-b border-red-600 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-red-600 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-white text-lg font-bold">IronCrypt</h1>
              
            </div>
          </div>
          <div className="flex items-center space-x-2 ml-8">
            <Shield className="w-4 h-4 text-blue-400" />
            <span className="text-white font-medium">AI-Powered Security Operations</span>
            <div className="flex items-center space-x-4 ml-6">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-blue-400 text-sm">LLM Enhanced</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-green-400 text-sm">AI Engine Active</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span className="text-yellow-400 text-sm">System Online</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-green-400 text-sm">Ready</span>
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-6">
          <div className="flex space-x-2">
            <span className="text-white text-sm"></span>
            <span className="text-gray-400"></span>
            <span className="text-white text-sm"></span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
