
import { VulnerabilityData } from '../types/vulnerability';
import { toast } from 'sonner';

export const uploadAndAnalyzeFile = async (file: File): Promise<VulnerabilityData> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:5001/api/upload-and-analyze', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Failed to parse error response' }));
    throw new Error(errorData.error || `Server responded with ${response.status}`);
  }

  return response.json();
};

export const generatePlaybook = async (vulnerabilityData: VulnerabilityData): Promise<void> => {
  const response = await fetch('http://localhost:5001/api/generate-playbook', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(vulnerabilityData),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to generate playbook.');
  }
};

export const generateAiPlaybook = async (vulnerabilityData: VulnerabilityData): Promise<{ playbook: string }> => {
  const response = await fetch('http://localhost:5001/api/generate-ai-playbook', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(vulnerabilityData),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to generate AI playbook.');
  }
  return response.json();
};

export const savePlaybook = async (playbook: string): Promise<void> => {
  const response = await fetch('http://localhost:5001/api/save-playbook', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ playbook }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to save playbook.');
  }
};

export const generateDocumentation = async (vulnerability: any, reportType: 'executive_summary' | 'technical_report') => {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/generate-documentation`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ vulnerability, reportType }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to generate documentation.');
  }

  const data = await response.json();
  return data.content;
};

export const recommendPatchWithContext = async (vulnerability: any): Promise<string> => {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/recommend-patch-with-context`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ vulnerability }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to get patch recommendation.');
  }

  const data = await response.json();
  return data.recommendation;
};

export const recommendPatch = async (vulnerability: any): Promise<string> => {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/recommend-patch`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ vulnerability }),
  });

  if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get patch recommendation.');
  }

  const data = await response.json();
  return data.recommendation;
};

export const getPatches = async (): Promise<{ name: string; tag: string }[]> => {
  const response = await fetch('http://localhost:5001/api/patches');
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to get patches.');
  }
  return response.json();
};

export const triggerPatch = async (tag?: string): Promise<{ patch_id: string }> => {
  const response = await fetch('http://localhost:5001/api/trigger-patch', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ tag }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to trigger patch.');
  }
  return response.json();
};

export const getPatchStatus = async (patchId: string): Promise<{ status: string; stdout?: string; stderr?: string }> => {
  const response = await fetch(`http://localhost:5001/api/patch-status/${patchId}`);
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to get patch status.');
  }
  return response.json();
};

export const listPatchLogs = async (): Promise<string[]> => {
  const response = await fetch('http://localhost:5001/api/logs');
  if (!response.ok) {
    throw new Error('Failed to list patch logs.');
  }
  return response.json();
};

export const downloadPatchLog = async (patchId: string) => {
  const response = await fetch(`http://localhost:5001/api/logs/${patchId}`);
  if (!response.ok) {
    toast.error('Failed to download log file.');
    return;
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${patchId}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};
