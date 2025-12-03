import { useState } from 'react';
import { Dialog } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { useExportStore } from '@/stores/exportStore';
import type { ExportFormat, ExportRequest } from '@/types/export';
import {
  X,
  Download,
  FileJson,
  FileText,
  FileCode,
  FileType,
  Check,
  Loader2,
  AlertCircle,
} from 'lucide-react';

interface ExportProjectDialogProps {
  projectId: string;
  projectName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const formatOptions: Array<{
  value: ExportFormat;
  label: string;
  description: string;
  icon: React.ElementType;
}> = [
  {
    value: 'json',
    label: 'JSON',
    description: 'Machine-readable format with full project data',
    icon: FileJson,
  },
  {
    value: 'markdown',
    label: 'Markdown',
    description: 'Human-readable text format for documentation',
    icon: FileText,
  },
  {
    value: 'html',
    label: 'HTML',
    description: 'Web-viewable format with styling',
    icon: FileCode,
  },
  {
    value: 'pdf',
    label: 'PDF',
    description: 'Print-ready document format',
    icon: FileType,
  },
];

export function ExportProjectDialog({
  projectId,
  projectName,
  open,
  onOpenChange,
}: ExportProjectDialogProps) {
  const { createExport, currentExport, downloadExport } = useExportStore();
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('markdown');
  const [options, setOptions] = useState({
    include_code: true,
    include_outputs: true,
    include_visualizations: true,
  });
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    setError(null);

    const exportRequest: ExportRequest = {
      project_id: projectId,
      format: selectedFormat,
      ...options,
    };

    try {
      await createExport(exportRequest);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create export');
    }
  };

  const handleDownload = async () => {
    if (!currentExport) return;

    try {
      await downloadExport(currentExport.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download export');
    }
  };

  const handleClose = () => {
    setError(null);
    onOpenChange(false);
  };

  const getStatusDisplay = () => {
    if (!currentExport) return null;

    switch (currentExport.status) {
      case 'pending':
      case 'processing':
        return (
          <Card className="p-4 bg-blue-500/10 border-blue-500">
            <div className="flex items-center gap-3">
              <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
              <div>
                <p className="font-medium text-blue-600">
                  {currentExport.status === 'pending' ? 'Queued' : 'Processing'}
                </p>
                <p className="text-sm text-muted-foreground">
                  Your export is being prepared...
                </p>
              </div>
            </div>
          </Card>
        );

      case 'completed':
        return (
          <Card className="p-4 bg-green-500/10 border-green-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Check className="h-5 w-5 text-green-600" />
                <div>
                  <p className="font-medium text-green-600">Export Complete</p>
                  <p className="text-sm text-muted-foreground">
                    Your file is ready to download
                  </p>
                </div>
              </div>
              <Button onClick={handleDownload} size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </Card>
        );

      case 'failed':
        return (
          <Card className="p-4 bg-destructive/10 border-destructive">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-destructive" />
              <div>
                <p className="font-medium text-destructive">Export Failed</p>
                <p className="text-sm text-muted-foreground">
                  {currentExport.error || 'An error occurred during export'}
                </p>
              </div>
            </div>
          </Card>
        );
    }
  };

  const canExport =
    !currentExport ||
    currentExport.status === 'completed' ||
    currentExport.status === 'failed';

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <div className="bg-card p-6 rounded-lg shadow-lg max-w-2xl w-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <Download className="h-5 w-5 text-primary" />
              Export Project
            </h2>
            <p className="text-sm text-muted-foreground mt-1">{projectName}</p>
          </div>
          <button
            onClick={handleClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-destructive/10 border border-destructive text-destructive px-3 py-2 rounded text-sm mb-4">
            {error}
          </div>
        )}

        {/* Status Display */}
        {currentExport && currentExport.project_id === projectId && (
          <div className="mb-6">{getStatusDisplay()}</div>
        )}

        {/* Format Selection */}
        <div className="space-y-4 mb-6">
          <Label>Export Format</Label>
          <div className="grid grid-cols-2 gap-3">
            {formatOptions.map((format) => {
              const Icon = format.icon;
              const isSelected = selectedFormat === format.value;

              return (
                <button
                  key={format.value}
                  onClick={() => setSelectedFormat(format.value)}
                  disabled={!canExport}
                  className={`relative p-4 rounded-lg border-2 transition-all text-left ${
                    isSelected
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  } ${!canExport ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  {isSelected && (
                    <div className="absolute top-2 right-2">
                      <Check className="h-4 w-4 text-primary" />
                    </div>
                  )}

                  <div className="flex items-start gap-3">
                    <div
                      className={`p-2 rounded-lg ${
                        isSelected ? 'bg-primary/10' : 'bg-muted'
                      }`}
                    >
                      <Icon
                        className={`h-5 w-5 ${
                          isSelected ? 'text-primary' : 'text-muted-foreground'
                        }`}
                      />
                    </div>

                    <div>
                      <p className="font-medium mb-1">{format.label}</p>
                      <p className="text-xs text-muted-foreground">
                        {format.description}
                      </p>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Export Options */}
        <div className="space-y-3 mb-6">
          <Label>Include in Export</Label>
          <Card className="p-4 space-y-3">
            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <p className="font-medium">Code Cells</p>
                <p className="text-sm text-muted-foreground">
                  Include all code content
                </p>
              </div>
              <input
                type="checkbox"
                checked={options.include_code}
                onChange={(e) =>
                  setOptions({ ...options, include_code: e.target.checked })
                }
                disabled={!canExport}
                className="h-4 w-4"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <p className="font-medium">Execution Outputs</p>
                <p className="text-sm text-muted-foreground">
                  Include cell execution results
                </p>
              </div>
              <input
                type="checkbox"
                checked={options.include_outputs}
                onChange={(e) =>
                  setOptions({ ...options, include_outputs: e.target.checked })
                }
                disabled={!canExport}
                className="h-4 w-4"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <p className="font-medium">Visualizations</p>
                <p className="text-sm text-muted-foreground">
                  Include charts and plots
                </p>
              </div>
              <input
                type="checkbox"
                checked={options.include_visualizations}
                onChange={(e) =>
                  setOptions({
                    ...options,
                    include_visualizations: e.target.checked,
                  })
                }
                disabled={!canExport}
                className="h-4 w-4"
              />
            </label>
          </Card>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleClose}
            className="flex-1"
          >
            Close
          </Button>
          <Button
            onClick={handleExport}
            disabled={!canExport}
            className="flex-1"
          >
            <Download className="h-4 w-4 mr-2" />
            {currentExport && currentExport.status === 'processing'
              ? 'Exporting...'
              : 'Start Export'}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
