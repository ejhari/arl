import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ArrowLeft, Upload, FileText, Trash2, Search, Calendar, FileType } from 'lucide-react';
import { documentsAPI } from '@/api/documents';
import { useCanvasStore } from '@/stores/canvasStore';
import { DocumentUploadDialog } from '@/components/documents/DocumentUploadDialog';
import { DocumentViewer } from '@/components/documents/DocumentViewer';
import type { Document, DocumentWithAnnotations, Annotation } from '@/types/document';

export function DocumentsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { projects, currentProject, loadProject } = useCanvasStore();

  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<DocumentWithAnnotations | null>(null);
  const [loading, setLoading] = useState(true);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const project = currentProject?.id === projectId ? currentProject : projects.find(p => p.id === projectId);

  useEffect(() => {
    if (projectId) {
      // Load project if not already loaded
      if (!project) {
        loadProject(projectId);
      }
      loadDocuments();
    }
  }, [projectId]);

  const loadDocuments = async () => {
    if (!projectId) return;

    setLoading(true);
    try {
      const docs = await documentsAPI.listDocuments(projectId);
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentSelect = async (documentId: string) => {
    try {
      const doc = await documentsAPI.getDocument(documentId);
      setSelectedDocument(doc);
    } catch (error) {
      console.error('Failed to load document:', error);
    }
  };

  const handleUploadSuccess = (document: Document) => {
    setDocuments((prev) => [document, ...prev]);
    setShowUploadDialog(false);
  };

  const handleDelete = async (documentId: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    setDeletingId(documentId);
    try {
      await documentsAPI.deleteDocument(documentId);
      setDocuments((prev) => prev.filter((d) => d.id !== documentId));
      if (selectedDocument?.id === documentId) {
        setSelectedDocument(null);
      }
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('Failed to delete document');
    } finally {
      setDeletingId(null);
    }
  };

  const handleAnnotationCreate = (annotation: Annotation) => {
    if (selectedDocument) {
      setSelectedDocument({
        ...selectedDocument,
        annotations: [...(selectedDocument.annotations || []), annotation],
      });
    }
  };

  const handleAnnotationDelete = (annotationId: string) => {
    if (selectedDocument) {
      setSelectedDocument({
        ...selectedDocument,
        annotations: (selectedDocument.annotations || []).filter((a) => a.id !== annotationId),
      });
    }
  };

  const filteredDocuments = documents.filter((doc) =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate(`/canvas/${projectId}`)}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Canvas
            </Button>
            <div>
              <h1 className="text-2xl font-bold">Research Library</h1>
              {project && <p className="text-sm text-muted-foreground">{project.name}</p>}
            </div>
          </div>
          <Button onClick={() => setShowUploadDialog(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Upload Document
          </Button>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Documents List Sidebar */}
        <div className="w-80 border-r bg-card flex flex-col">
          {/* Search */}
          <div className="p-4 border-b">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          {/* Documents List */}
          <div className="flex-1 overflow-auto">
            {loading ? (
              <div className="flex items-center justify-center p-8">
                <div className="text-muted-foreground">Loading documents...</div>
              </div>
            ) : filteredDocuments.length === 0 ? (
              <div className="flex flex-col items-center justify-center p-8 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mb-3" />
                <p className="text-muted-foreground">
                  {searchQuery ? 'No documents found' : 'No documents yet'}
                </p>
                {!searchQuery && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-4"
                    onClick={() => setShowUploadDialog(true)}
                  >
                    Upload Your First Document
                  </Button>
                )}
              </div>
            ) : (
              <div className="p-2 space-y-1">
                {filteredDocuments.map((doc) => (
                  <Card
                    key={doc.id}
                    className={`p-3 cursor-pointer transition-colors hover:bg-muted/50 ${
                      selectedDocument?.id === doc.id ? 'bg-muted border-primary' : ''
                    }`}
                    onClick={() => handleDocumentSelect(doc.id)}
                  >
                    <div className="flex items-start gap-3">
                      <FileText className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-sm truncate">{doc.title}</h3>
                        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                          <FileType className="h-3 w-3" />
                          <span>{doc.file_type.split('/')[1]?.toUpperCase() || 'FILE'}</span>
                          <span>•</span>
                          <span>{formatFileSize(doc.file_size)}</span>
                        </div>
                        <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                          <Calendar className="h-3 w-3" />
                          <span>{formatDate(doc.created_at)}</span>
                        </div>
                        {doc.is_processed && doc.page_count && (
                          <div className="text-xs text-muted-foreground mt-1">
                            {doc.page_count} pages
                          </div>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(doc.id);
                        }}
                        disabled={deletingId === doc.id}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Stats Footer */}
          <div className="border-t p-4 bg-muted/30">
            <div className="text-sm text-muted-foreground">
              {documents.length} document{documents.length !== 1 ? 's' : ''} total
            </div>
          </div>
        </div>

        {/* Document Viewer */}
        <div className="flex-1 overflow-hidden p-6">
          {selectedDocument ? (
            <DocumentViewer
              document={selectedDocument}
              onAnnotationCreate={handleAnnotationCreate}
              onAnnotationDelete={handleAnnotationDelete}
            />
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No Document Selected</h3>
                <p className="text-muted-foreground mb-6">
                  Select a document from the list to view and annotate
                </p>
                {documents.length === 0 && (
                  <Button onClick={() => setShowUploadDialog(true)}>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Document
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Upload Dialog */}
      {showUploadDialog && projectId && (
        <DocumentUploadDialog
          projectId={projectId}
          onUploadSuccess={handleUploadSuccess}
          onClose={() => setShowUploadDialog(false)}
        />
      )}
    </div>
  );
}
