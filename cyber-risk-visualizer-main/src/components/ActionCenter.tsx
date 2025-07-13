
import React from 'react';
import { Shield, ChevronDown } from 'lucide-react';

const PatchManagementSystem = () => {
  return (
    <div className="bg-gradient-to-r from-red-600 to-red-800 rounded-lg p-6 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-white text-xl font-bold">LLM Patch Management System</h2>
            <p className="text-red-100 text-sm">AI-Driven Vulnerability Assessment & Remediation</p>
          </div>
        </div>
        <ChevronDown className="w-6 h-6 text-white" />
      </div>
      <div className="mt-6 text-white text-sm">
        <h3 className="font-semibold mb-2">System Overview</h3>
        <p className="text-red-100 mb-4">
          Our LLM-powered patch management system combines traditional network scanning with cutting-edge artificial intelligence to provide comprehensive vulnerability 
          assessment and automated remediation recommendations. The system leverages large language models to understand security contexts, analyze threat patterns, 
          and generate actionable security patches.
        </p>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-white rounded-full mt-2"></div>
            <div>
              <h4 className="font-medium">AI-Powered Analysis</h4>
              <p className="text-red-200 text-xs">Advanced LLM engine analyzes vulnerabilities and generates contextual security insights</p>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-red-400 rounded-full mt-2"></div>
            <div>
              <h4 className="font-medium">Intelligent Prioritization</h4>
              <p className="text-red-200 text-xs">Machine learning algorithms automatically prioritize threats based on risk assessment</p>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-red-300 rounded-full mt-2"></div>
            <div>
              <h4 className="font-medium">Automated Patch Generation</h4>
              <p className="text-red-200 text-xs">AI generates specific patch commands and remediation steps for identified vulnerabilities</p>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-white rounded-full mt-2"></div>
            <div>
              <h4 className="font-medium">Comprehensive Reporting</h4>
              <p className="text-red-200 text-xs">Detailed markdown reports with executive summaries and technical recommendations</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatchManagementSystem;
