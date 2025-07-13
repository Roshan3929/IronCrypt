import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

interface FileUploadProps {
  onAnalyze: (file: File) => void;
  loading: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onAnalyze, loading }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/xml') {
      setSelectedFile(file);
    } else {
      setSelectedFile(null);
      toast.error('Invalid file type. Please upload an XML file.');
    }
  };

  const handleAnalyzeClick = () => {
    if (selectedFile) {
      onAnalyze(selectedFile);
    } else {
      toast.warning('Please select an XML file to analyze.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900">
      <Card className="w-full max-w-lg bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white">Upload Nmap Scan Report</CardTitle>
          <CardDescription>Select an XML file from your local machine to begin the analysis.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Input
              type="file"
              onChange={handleFileChange}
              accept=".xml,text/xml"
              className="text-gray-300 file:text-gray-300 file:bg-gray-700"
            />
            <Button onClick={handleAnalyzeClick} disabled={loading || !selectedFile} className="w-full">
              {loading ? 'Analyzing...' : 'Analyze'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FileUpload; 