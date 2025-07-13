import React, { useRef, useState, useEffect } from 'react';
import html2canvas from 'html2canvas';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from '@/components/ui/hover-card';
import { cn } from '@/lib/utils';
import { VulnerabilityData, ProcessedVulnerability } from '@/types/vulnerability';

// A new type that links a vulnerability to a room
interface MappedVulnerability extends ProcessedVulnerability {
  room: string;
}

// Helper to shuffle an array
const shuffleArray = <T,>(array: T[]): T[] => {
  return [...array].sort(() => Math.random() - 0.5);
};

// 1. Room to Coordinate Mapping (as percentages) remains the same
const roomCoordinates: Record<string, { top: string; left: string }> = {
  "Room 1": { top: "25%", left: "18%" },
  "Room 4": { top: "25%", left: "39%" },
  "Room 7": { top: "25%", left: "70%" },
  "Room 10": { top: "76%", left: "25%" },
  "Conference Room": { top: "76%", left: "45%" },
  "Server Room": { top: "76%", left: "70%" },
  "Room 3": { top: "20%", left: "85%"},
  "Room 2": { top: "35%", left: "85%"},
  "Room 5": { top: "48%", left: "85%"},
  "Room 6": { top: "60%", left: "85%"}
};

// 2. Helper function for severity color
const getSeverityColor = (cvss: number) => {
  if (cvss >= 9.0) return 'bg-red-500/80 border-red-400';
  if (cvss >= 7.0) return 'bg-orange-500/80 border-orange-400';
  if (cvss >= 4.0) return 'bg-yellow-500/80 border-yellow-400';
  return 'bg-green-500/80 border-green-400';
};

const getSeverityGlow = (cvss: number) => {
    if (cvss >= 9.0) return 'shadow-[0_0_15px_5px_rgba(239,68,68,0.7)]';
    if (cvss >= 7.0) return 'shadow-[0_0_15px_5px_rgba(249,115,22,0.7)]';
    if (cvss >= 4.0) return 'shadow-[0_0_15px_5px_rgba(234,179,8,0.7)]';
    return 'shadow-[0_0_15px_5px_rgba(34,197,94,0.7)]';
}

interface FloorplanVisualizerProps {
    data: VulnerabilityData | null;
}

const FloorplanVisualizer: React.FC<FloorplanVisualizerProps> = ({ data }) => {
    const printRef = useRef<HTMLDivElement>(null);
    const [mappedVulnerabilities, setMappedVulnerabilities] = useState<MappedVulnerability[]>([]);

    useEffect(() => {
        if (!data) return;

        // Flatten the complex data structure into a list of vulnerabilities
        const allVulnerabilities: ProcessedVulnerability[] = Object.entries(data).flatMap(([hostIp, hostData]) => 
            hostData.services.flatMap(service => 
                service.vulnerabilities.map(vuln => ({
                    ...vuln,
                    host_ip: hostIp,
                    os: hostData.os,
                    port: service.port,
                    service_name: service.service_name,
                    version: service.version,
                }))
            )
        );

        // Shuffle rooms and map vulnerabilities to them
        const availableRooms = shuffleArray(Object.keys(roomCoordinates));
        const newMappedVulnerabilities = allVulnerabilities
            .slice(0, availableRooms.length) // Ensure we don't exceed available rooms
            .map((vuln, index) => ({
                ...vuln,
                room: availableRooms[index],
            }));
        
        setMappedVulnerabilities(newMappedVulnerabilities);

    }, [data]);

    const handleExport = () => {
        const element = printRef.current;
        if (element) {
            html2canvas(element, {
                useCORS: true,
                backgroundColor: null,
            }).then((canvas) => {
                const link = document.createElement('a');
                link.download = 'floorplan-vulnerabilities.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            });
        }
    };
  return (
    <Card className="bg-white text-gray-900">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Office Floorplan Visualizer</CardTitle>
        <Button onClick={handleExport}>Export as PNG</Button>
      </CardHeader>
      <CardContent>
        <div ref={printRef} className="relative w-full max-w-6xl mx-auto">
          <img src="/WhatsApp Image 2025-07-13 at 01.43.06.png" alt="Office Floorplan" className="w-full h-auto rounded-lg" />

          {/* Render Vulnerability Nodes */}
          {mappedVulnerabilities.map((node) => {
          const coords = roomCoordinates[node.room];
          if (!coords) return null;

          return (
            <HoverCard key={`${node.host_ip}-${node.cve_id}`}>
              <HoverCardTrigger asChild>
                <div
                  className={cn(
                    'absolute w-5 h-5 rounded-full transform -translate-x-1/2 -translate-y-1/2 cursor-pointer border-2 transition-all duration-300 hover:scale-125',
                    getSeverityColor(node.cvss_score),
                    getSeverityGlow(node.cvss_score),
                  )}
                  style={{ top: coords.top, left: coords.left }}
                />
              </HoverCardTrigger>
              <HoverCardContent className="w-80 bg-white border-gray-200 text-gray-900">
                <div className="space-y-2">
                  <h4 className="font-bold">{node.room}</h4>
                  <p><strong>IP Address:</strong> {node.host_ip}</p>
                  <p><strong>CVE:</strong> {node.cve_id}</p>
                  <p><strong>Service:</strong> {node.service_name} {node.version}</p>
                  <p>
                    <strong>CVSS Score:</strong> 
                    <span className={cn('font-bold', getSeverityColor(node.cvss_score).split(' ')[0].replace('bg-', 'text-').replace('/80', ''))}>
                         {' '}{node.cvss_score}
                    </span>
                  </p>
                </div>
              </HoverCardContent>
            </HoverCard>
          );
        })}
        {/* Legend */}
        <div className="absolute bottom-4 right-4 bg-gray-100/80 p-3 rounded-lg text-gray-900 text-sm">
            <h4 className="font-bold mb-2">Severity Legend</h4>
            <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded-full bg-red-500"></div>
                <span>Critical (≥ 9.0)</span>
            </div>
            <div className="flex items-center space-x-2 mt-1">
                <div className="w-4 h-4 rounded-full bg-orange-500"></div>
                <span>High (7.0-8.9)</span>
            </div>
            <div className="flex items-center space-x-2 mt-1">
                <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
                <span>Medium (4.0-6.9)</span>
            </div>
            <div className="flex items-center space-x-2 mt-1">
                <div className="w-4 h-4 rounded-full bg-green-500"></div>
                <span>Low (&lt; 4.0)</span>
            </div>
        </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default FloorplanVisualizer; 