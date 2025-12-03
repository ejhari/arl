import { FileText, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function DocumentsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground mt-1">
            Manage and annotate your research documents
          </p>
        </div>
        <Button>
          <Upload className="h-4 w-4 mr-2" />
          Upload Document
        </Button>
      </div>

      {/* Placeholder */}
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
        <div className="bg-muted rounded-full p-6 mb-4">
          <FileText className="h-12 w-12 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold mb-2">Document Management</h3>
        <p className="text-muted-foreground mb-4 max-w-sm">
          Document management features are coming soon. You'll be able to upload,
          view, annotate, and extract citations from PDFs and other documents.
        </p>
      </div>
    </div>
  );
}
