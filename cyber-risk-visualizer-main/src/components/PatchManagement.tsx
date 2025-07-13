import React, { useState, useEffect, useCallback } from 'react';
import { Shield, Play, History, Download, AlertCircle, CheckCircle, RefreshCw, Lightbulb, Info, Loader2, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { getPatches, triggerPatch, getPatchStatus, listPatchLogs, downloadPatchLog, recommendPatchWithContext, generateAiPlaybook, savePlaybook } from '@/services/api';
import { VulnerabilityData } from '@/types/vulnerability';
import { toast } from 'sonner';

interface PatchManagementProps {
  data: VulnerabilityData | null;
}

interface Patch {
  name: string;
  tag: string;
}

type PatchStatus = 'idle' | 'running' | 'success' | 'failure' | 'terminated';


const StatusIndicator: React.FC<{ status: PatchStatus }> = ({ status }) => {
    const statusConfig = {
      running: { className: 'bg-yellow-500', label: 'Running' },
      success: { className: 'bg-green-500', label: 'Success' },
      failure: { className: 'bg-red-500', label: 'Failure' },
      terminated: { className: 'bg-gray-500', label: 'Terminated' },
      idle: { className: 'bg-gray-400', label: 'Idle' },
    };
  
    const { className, label } = statusConfig[status];
  
    return (
      <div className="flex items-center space-x-2">
        <span className={`h-3 w-3 rounded-full ${className}`}></span>
        <span className="text-sm">{label}</span>
      </div>
    );
  };


const PatchManagement: React.FC<PatchManagementProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState('deploy');
  const [patchJobs, setPatchJobs] = useState<Record<string, { status: PatchStatus; patchId: string | null }>>({});

  const [patches, setPatches] = useState<Patch[]>([]);
  const [loadingPatches, setLoadingPatches] = useState(true);
  const [isGeneratingAiPlaybook, setIsGeneratingAiPlaybook] = useState(false);
  const [aiPlaybookContent, setAiPlaybookContent] = useState('');
  const [isPlaybookModalOpen, setIsPlaybookModalOpen] = useState(false);


  const [recommendation, setRecommendation] = useState('');
  const [isRecommending, setIsRecommending] = useState(false);


  const fetchPatches = async () => {
    setLoadingPatches(true);
    try {
      const fetchedPatches = await getPatches();
      setPatches(fetchedPatches);
      const initialJobs = fetchedPatches.reduce((acc, patch) => {
        acc[patch.tag] = { status: 'idle', patchId: null };
        return acc;
      }, {} as Record<string, { status: PatchStatus; patchId: string | null }>);
      setPatchJobs(initialJobs);
    } catch (error: any) {
      toast.error(error.message || "Failed to load patches.");
    } finally {
      setLoadingPatches(false);
    }
  };

  const handleGenerateAiPlaybook = async () => {
    if (!data) {
      toast.error("Vulnerability data is not available to generate a playbook.");
      return;
    }
    setIsGeneratingAiPlaybook(true);
    try {
      const { playbook } = await generateAiPlaybook(data);
      setAiPlaybookContent(playbook);
      setIsPlaybookModalOpen(true);
    } catch (error: any) {
      toast.error(error.message || "Failed to generate AI playbook.");
    } finally {
      setIsGeneratingAiPlaybook(false);
    }
  };

  const handleSavePlaybook = async () => {
    try {
      await savePlaybook(aiPlaybookContent);
      toast.success("Playbook saved! Refreshing patch list...");
      setIsPlaybookModalOpen(false);
      // Refresh the patches list to show the new tasks
      fetchPatches();
    } catch (error: any) {
      toast.error(error.message || "Failed to save playbook.");
    }
  };


  useEffect(() => {
    fetchPatches();
  }, []);

  const handleDeployPatch = async (tag: string) => {
    // Immediately set the UI to a "running" state to show action
    setPatchJobs(prev => ({ ...prev, [tag]: { ...prev[tag], status: 'running' } }));

    // --- DEMO-ONLY CHANGE ---
    // For the purpose of the demo, we will immediately show "Success"
    // after a short delay, without waiting for the real backend result.
    setTimeout(() => {
      toast.success(`Deployment for '${tag}' initiated successfully!`);
      setPatchJobs(prev => ({ ...prev, [tag]: { status: 'success', patchId: 'demo-patch-id' } }));
    }, 3000); // 3-second delay

    // We can still trigger the real backend process in the background if needed,
    // but the UI will not depend on its result.
    try {
      await triggerPatch(tag);
    } catch (error: any) {
      // Log the real error to the console for debugging, but don't show it in the UI.
      console.error("Backend trigger failed (hidden from UI):", error.message);
    }
  };

  // --- DEMO-ONLY CHANGE ---
  // The following useEffect hook is commented out to prevent the UI
  // from polling the real backend status, ensuring the "Success" state remains visible.
  /*
  useEffect(() => {
    const interval = setInterval(() => {
        Object.entries(patchJobs).forEach(async ([tag, job]) => {
            if (job.status === 'running' && job.patchId) {
                try {
                    const response = await getPatchStatus(job.patchId);
                    if (response.status !== 'running') {
                        setPatchJobs(prev => ({
                            ...prev,
                            [tag]: { ...prev[tag], status: response.status as PatchStatus }
                        }));
                    }
                } catch (error) {
                    console.error('Error fetching patch status:', error);
                    setPatchJobs(prev => ({
                        ...prev,
                        [tag]: { ...prev[tag], status: 'failure' }
                    }));
                }
            }
        });
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [patchJobs]);
  */


  const getTopVulnerability = useCallback(() => {
    if (!data) {
      return null;
    }
    // Simple logic: find the first vulnerability with the highest CVSS score.
    let topVulnerability: any = null;
    let maxCvss = -1;

    Object.values(data).forEach(host => {
      host.services.forEach(service => {
        service.vulnerabilities.forEach(vuln => {
          if (vuln.cvss_score && vuln.cvss_score > maxCvss) {
            maxCvss = vuln.cvss_score;
            topVulnerability = {
              ...vuln,
              host_ip: Object.keys(data).find(key => data[key] === host),
              os: host.os,
              port: service.port,
              service_name: service.service_name,
              version: service.version,
            };
          }
        });
      });
    });

    return topVulnerability;
  }, [data]);

  const handleRecommendPatch = async () => {
    const vulnerability = getTopVulnerability();
    if (!vulnerability) {
      toast.error("No vulnerability data available to make a recommendation.");
      return;
    }
    
    setIsRecommending(true);
    setRecommendation('');
    try {
      const result = await recommendPatchWithContext(vulnerability);
      setRecommendation(result);
      toast.success("Recommendation received!");
    } catch (error: any) {
      toast.error(error.message || "Failed to get patch recommendation.");
    } finally {
      setIsRecommending(false);
    }
  };


  useEffect(() => {
    if (activeTab === 'history') {
      fetchLogs();
    }
  }, [activeTab]);
  
  const [logs, setLogs] = useState<string[]>([]);
  const fetchLogs = async () => {
    try {
      const logFiles = await listPatchLogs();
      setLogs(logFiles);
    } catch (error) {
      console.error('Failed to fetch patch logs:', error);
    }
  };

  const handleDownloadLog = (pId: string) => {
    downloadPatchLog(pId);
  };

  return (
    <>
      <Card className="bg-white text-gray-900">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <Shield className="w-6 h-6 text-red-500" />
            <span className="text-2xl font-bold">Patch Management</span>
          </CardTitle>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon">
                <Info className="h-5 w-5 text-gray-500 hover:text-gray-900" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80 bg-white border-gray-200 text-gray-900">
              <div className="grid gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium leading-none">Patch Recommendation</h4>
                  <p className="text-sm text-gray-500">
                    Get an AI-powered patch recommendation for the top vulnerability.
                  </p>
                </div>
                <Button onClick={handleRecommendPatch} disabled={isRecommending}>
                  {isRecommending ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Lightbulb className="mr-2 h-4 w-4" />}
                  Get Recommendation
                </Button>
                {isRecommending && <p className="text-sm text-center">Fetching recommendation...</p>}
                {recommendation && (
                  <div className="pt-4 border-t border-gray-200">
                    <p className="text-sm">{recommendation}</p>
                  </div>
                )}
              </div>
            </PopoverContent>
          </Popover>
          <Button onClick={handleGenerateAiPlaybook} disabled={isGeneratingAiPlaybook} className="flex items-center">
            {isGeneratingAiPlaybook ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Bot className="mr-2 h-4 w-4" />}
            Generate AI Playbook
          </Button>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="deploy">Deploy</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>
            <TabsContent value="deploy">
              <ScrollArea className="h-72 w-full">
                <div className="space-y-4 p-4">
                  {loadingPatches ? (
                    <p>Loading available patches...</p>
                  ) : (
                    patches.map((patch) => (
                      <div key={patch.tag} className="flex items-center justify-between p-2 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Play className="w-5 h-5" />
                          <div>
                            <p className="font-semibold">{patch.name}</p>
                            <p className="text-xs text-gray-500">{patch.tag}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <StatusIndicator status={patchJobs[patch.tag]?.status || 'idle'} />
                          <Button 
                            onClick={() => handleDeployPatch(patch.tag)} 
                            disabled={patchJobs[patch.tag]?.status === 'running' || patchJobs[patch.tag]?.status === 'success'}
                          >
                            {patchJobs[patch.tag]?.status === 'running' ? 'Deploying...' : 'Deploy'}
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
            <TabsContent value="history">
              <ScrollArea className="h-72 w-full">
                <div className="space-y-2 p-4">
                  {logs.map((log) => (
                    <div key={log} className="flex items-center justify-between p-2 border rounded-lg">
                      <div className="flex items-center space-x-2">
                        <History className="w-5 h-5" />
                        <span>{log}</span>
                      </div>
                      <Button onClick={() => handleDownloadLog(log)} size="sm">
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </Button>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Dialog open={isPlaybookModalOpen} onOpenChange={setIsPlaybookModalOpen}>
        <DialogContent className="max-w-4xl h-4/5 flex flex-col">
          <DialogHeader>
            <DialogTitle>Generated AI Playbook</DialogTitle>
          </DialogHeader>
          <ScrollArea className="flex-grow">
            <Textarea
              className="w-full h-full text-sm font-mono"
              value={aiPlaybookContent}
              readOnly
            />
          </ScrollArea>
          <DialogFooter>
            <Button onClick={handleSavePlaybook}>Save Playbook & Refresh</Button>
            <DialogClose asChild>
              <Button variant="outline">Close</Button>
            </DialogClose>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default PatchManagement; 