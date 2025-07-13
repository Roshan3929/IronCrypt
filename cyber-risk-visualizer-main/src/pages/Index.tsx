import React, { useState } from 'react';
import Header from '../components/Header';
import VulnerabilityDashboard from '../components/VulnerabilityDashboard';
import FileUpload from '../components/FileUpload';
import LoadingSpinner from '../components/LoadingSpinner';
import { uploadAndAnalyzeFile, generatePlaybook } from '../services/api';
import { VulnerabilityData } from '../types/vulnerability';
import { toast } from 'sonner';
import { Chatbot } from '@/components/Chatbot';
import FloorplanVisualizer from '@/components/FloorplanVisualizer';
import PatchManagement from '@/components/PatchManagement';

type AppStatus = 'idle' | 'loading' | 'success' | 'error';

const Index = () => {
  const [status, setStatus] = useState<AppStatus>('idle');
  const [vulnerabilityData, setVulnerabilityData] = useState<VulnerabilityData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (file: File) => {
    setStatus('loading');
    setError(null);
    try {
      const data = await uploadAndAnalyzeFile(file);
      if (Object.keys(data).length === 0) {
        toast.error('Analysis returned no data. Please check the scan file.');
        setStatus('idle');
      } else {
        await generatePlaybook(data); // Generate the playbook
        setVulnerabilityData(data);
        setStatus('success');
        toast.success('Analysis complete and playbook generated!');
      }
    } catch (err: any) {
      const errorMessage = err.message || 'An unknown error occurred.';
      setError(errorMessage);
      setStatus('error');
      toast.error(errorMessage);
    }
  };

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return <LoadingSpinner />;
      case 'success':
        // Use flexbox with gap for consistent spacing
        return (
          <div className="flex flex-col gap-4">
            <VulnerabilityDashboard data={vulnerabilityData} loading={false} />
            <FloorplanVisualizer data={vulnerabilityData} />
            <PatchManagement data={vulnerabilityData} />
          </div>
        );
      case 'error':
        return (
          <div className="text-center text-red-400 p-8">
            <h2 className="text-2xl font-bold mb-4">Analysis Failed</h2>
            <p>{error}</p>
            <button onClick={() => setStatus('idle')} className="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg">
              Try Again
            </button>
          </div>
        );
      case 'idle':
      default:
        return <FileUpload onAnalyze={handleAnalyze} loading={false} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-900">
      <Header />
      <main className="flex-grow p-6">
        {renderContent()}
      </main>
      {status === 'success' && <Chatbot vulnerabilityData={vulnerabilityData} />}
    </div>
  );
};

export default Index;
