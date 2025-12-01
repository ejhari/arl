import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { X, Download, FileJson, FileText, FileCode, File } from 'lucide-react';
import { exportsAPI } from '@/api/exports';
import type { ExportFormat, ExportJob } from '@/types/export';

interface ExportDialogProps {
  projectId: string;
  onClose: () => void;
}

export function ExportDialog({ projectId, onClose }: ExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('markdown');
  const [includeCode, setIncludeCode] = useState(true);
  const [includeOutputs, setIncludeOutputs] = useState(true);
  const [includeVisualizations, setIncludeVisualizations] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [exportJob, setExportJob] = useState<ExportJob | null>(null);
  const [error, setError] = useState('');

  const formats: Array<{ value: ExportFormat; label: string; icon: any; description: string }> = [
    {
      value: 'json',
      label: 'JSON',
      icon: FileJson,
      description: 'Machine-readable data format',
    },
    {
      value: 'markdown',
      label: 'Markdown',
      icon: FileText,
      description: 'Human-readable text format',
    },
    {
      value: 'html',
      label: 'HTML',
      icon: FileCode,
      description: 'Web page with formatting',
    },
    {
      value: 'pdf',
      label: 'PDF',
      icon: File,
      description: 'Printable document (coming soon)',
    },
  ];

  const handleExport = async () => {
    setExporting(true);
    setError('');

    try {
      const job = await exportsAPI.createExport({
        project_id: projectId,
        format: selectedFormat,
        include_code: includeCode,
        include_outputs: includeOutputs,
        include_visualizations: includeVisualizations,
      });

      setExportJob(job);

      // Poll for completion (simple implementation)
      const pollInterval = setInterval(async () => {
        try {
          const updated = await exportsAPI.getExportStatus(job.id);
          setExportJob(updated);

          if (updated.status === 'completed' || updated.status === 'failed') {
            clearInterval(pollInterval);
            setExporting(false);

            if (updated.status === 'completed' && updated.download_url) {
              // Auto-download
              window.open(exportsAPI.getDownloadUrl(updated.id), '_blank');
            } else if (updated.status === 'failed') {
              setError(updated.error || 'Export failed');
            }
          }
        } catch (err) {
          clearInterval(pollInterval);
          setExporting(false);
          setError(err instanceof Error ? err.message : 'Failed to check export status');
        }
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
      setExporting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold">Export Project</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-6">
          {/* Format Selection */}
          <div>
            <Label className="text-base font-medium mb-3 block">Export Format</Label>
            <div className="grid grid-cols-2 gap-3">
              {formats.map((format) => (
                <button
                  key={format.value}
                  onClick={() => setSelectedFormat(format.value)}
                  disabled={format.value === 'pdf'}
                  className={`p-4 rounded-lg border-2 text-left transition-colors ${
                    selectedFormat === format.value
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  } ${format.value === 'pdf' ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <format.icon className="h-5 w-5" />
                    <span className="font-medium">{format.label}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">{format.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Options */}
          <div>
            <Label className="text-base font-medium mb-3 block">Include</Label>
            <div className="space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeCode}
                  onChange={(e) => setIncludeCode(e.target.checked)}
                  className="h-4 w-4"
                />
                <span className="text-sm">Code cells and execution results</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeOutputs}
                  onChange={(e) => setIncludeOutputs(e.target.checked)}
                  className="h-4 w-4"
                />
                <span className="text-sm">Cell outputs</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeVisualizations}
                  onChange={(e) => setIncludeVisualizations(e.target.checked)}
                  className="h-4 w-4"
                />
                <span className="text-sm">Visualizations and charts</span>
              </label>
            </div>
          </div>

          {/* Export Status */}
          {exportJob && (
            <div className="p-4 rounded-lg bg-muted">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Export Status</p>
                  <p className="text-sm text-muted-foreground capitalize">{exportJob.status}</p>
                </div>
                {exportJob.status === 'completed' && exportJob.download_url && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open(exportsAPI.getDownloadUrl(exportJob.id), '_blank')}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                )}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-4 rounded-lg bg-destructive/10 text-destructive text-sm">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={onClose} className="flex-1" disabled={exporting}>
              Cancel
            </Button>
            <Button onClick={handleExport} className="flex-1" disabled={exporting}>
              {exporting ? (
                <>Exporting...</>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
