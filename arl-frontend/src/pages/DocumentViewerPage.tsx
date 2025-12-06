import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentsAPI } from '@/api/documents';
import type { DocumentWithAnnotations, Annotation } from '@/types/document';
import { PDFViewer } from '@/components/documents/PDFViewer';
import { AnnotationsSidebar } from '@/components/documents/AnnotationsSidebar';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download } from 'lucide-react';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

export function DocumentViewerPage() {
  const { projectId, documentId } = useParams<{ projectId: string; documentId: string }>();
  const navigate = useNavigate();
  const [document, setDocument] = useState<DocumentWithAnnotations | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    if (documentId) {
      loadDocument();
    }
  }, [documentId]);

  const loadDocument = async () => {
    if (!documentId) return;

    setIsLoading(true);
    setError(null);

    try {
      const doc = await documentsAPI.getDocument(documentId);
      setDocument(doc);

      // Dispatch event for breadcrumbs to pick up document title
      window.dispatchEvent(
        new CustomEvent('document-loaded', { detail: { title: doc.title } })
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load document');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnnotationCreate = async (annotation: Omit<Annotation, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => {
    if (!documentId) return;

    try {
      const newAnnotation = await documentsAPI.createAnnotation({
        document_id: documentId,
        annotation_type: annotation.annotation_type,
        page_number: annotation.page_number,
        content: annotation.content || undefined,
        position: annotation.position || undefined,
        color: annotation.color || undefined,
      });

      setDocument((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          annotations: [...prev.annotations, newAnnotation],
        };
      });
    } catch (err) {
      console.error('Failed to create annotation:', err);
    }
  };

  const handleAnnotationDelete = async (annotationId: string) => {
    try {
      await documentsAPI.deleteAnnotation(annotationId);
      setDocument((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          annotations: prev.annotations.filter((a) => a.id !== annotationId),
        };
      });
    } catch (err) {
      console.error('Failed to delete annotation:', err);
    }
  };

  const handleAnnotationUpdate = async (annotationId: string, data: { content?: string }) => {
    try {
      const updatedAnnotation = await documentsAPI.updateAnnotation(annotationId, data);
      setDocument((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          annotations: prev.annotations.map((a) =>
            a.id === annotationId ? updatedAnnotation : a
          ),
        };
      });
    } catch (err) {
      console.error('Failed to update annotation:', err);
      throw err;
    }
  };

  const handleDownload = () => {
    if (!documentId) return;
    const url = documentsAPI.getDocumentDownloadUrl(documentId);
    window.open(url, '_blank');
  };

  const handleAnnotationClick = (annotation: Annotation) => {
    // Navigate to the page containing the annotation
    setCurrentPage(annotation.page_number);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-destructive mb-4">{error || 'Document not found'}</p>
        <Button onClick={() => navigate(`/documents/${projectId}`)}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Documents
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="border-b bg-background px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`/documents/${projectId}`)}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-lg font-semibold">{document.title}</h1>
            <p className="text-sm text-muted-foreground">{document.file_name}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSidebar(!showSidebar)}
          >
            {showSidebar ? 'Hide' : 'Show'} Annotations
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* PDF Viewer */}
        <div className="flex-1 overflow-auto bg-muted/30">
          <PDFViewer
            documentId={document.id}
            fileUrl={documentsAPI.getDocumentDownloadUrl(document.id)}
            annotations={document.annotations}
            onAnnotationCreate={handleAnnotationCreate}
            onAnnotationUpdate={handleAnnotationUpdate}
            currentPage={currentPage}
            onPageChange={setCurrentPage}
          />
        </div>

        {/* Annotations Sidebar */}
        {showSidebar && (
          <AnnotationsSidebar
            annotations={document.annotations}
            onAnnotationDelete={handleAnnotationDelete}
            onAnnotationClick={handleAnnotationClick}
          />
        )}
      </div>
    </div>
  );
}
