import { useState, useCallback } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Download } from 'lucide-react';
import type { Document as DocumentType, Annotation, CreateAnnotationData } from '@/types/document';
import { documentsAPI } from '@/api/documents';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface DocumentViewerProps {
  document: DocumentType & { annotations?: Annotation[] };
  onAnnotationCreate?: (annotation: Annotation) => void;
  onAnnotationDelete?: (annotationId: string) => void;
}

export function DocumentViewer({ document, onAnnotationCreate, onAnnotationDelete }: DocumentViewerProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);
  const [selectedText, setSelectedText] = useState<string>('');
  const [showAnnotationMenu, setShowAnnotationMenu] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });

  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setPageNumber(1);
  }, []);

  const goToPrevPage = () => setPageNumber((page) => Math.max(1, page - 1));
  const goToNextPage = () => setPageNumber((page) => Math.min(numPages, page + 1));
  const zoomIn = () => setScale((s) => Math.min(3.0, s + 0.2));
  const zoomOut = () => setScale((s) => Math.max(0.5, s - 0.2));

  const handleDownload = () => {
    const downloadUrl = documentsAPI.getDocumentDownloadUrl(document.id);
    window.open(downloadUrl, '_blank');
  };

  const handleTextSelect = (event: React.MouseEvent) => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 0) {
      setSelectedText(text);
      setMenuPosition({ x: event.clientX, y: event.clientY });
      setShowAnnotationMenu(true);
    } else {
      setShowAnnotationMenu(false);
    }
  };

  const createAnnotation = async (type: 'highlight' | 'comment' | 'note', color?: string) => {
    if (!selectedText) return;

    try {
      const annotationData: CreateAnnotationData = {
        document_id: document.id,
        annotation_type: type,
        page_number: pageNumber,
        content: selectedText,
        position: { x: menuPosition.x, y: menuPosition.y },
        color: color || '#ffeb3b',
      };

      const newAnnotation = await documentsAPI.createAnnotation(annotationData);
      onAnnotationCreate?.(newAnnotation);
      setShowAnnotationMenu(false);
      setSelectedText('');
    } catch (error) {
      console.error('Failed to create annotation:', error);
    }
  };

  const deleteAnnotation = async (annotationId: string) => {
    try {
      await documentsAPI.deleteAnnotation(annotationId);
      onAnnotationDelete?.(annotationId);
    } catch (error) {
      console.error('Failed to delete annotation:', error);
    }
  };

  const documentUrl = documentsAPI.getDocumentDownloadUrl(document.id);

  return (
    <div className="flex flex-col h-full bg-muted/30">
      {/* Toolbar */}
      <Card className="p-3 mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={goToPrevPage} disabled={pageNumber <= 1}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium">
            Page {pageNumber} of {numPages}
          </span>
          <Button variant="outline" size="sm" onClick={goToNextPage} disabled={pageNumber >= numPages}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={zoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium">{Math.round(scale * 100)}%</span>
          <Button variant="outline" size="sm" onClick={zoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>

        <Button variant="outline" size="sm" onClick={handleDownload}>
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
      </Card>

      {/* PDF Viewer */}
      <div
        className="flex-1 overflow-auto flex justify-center p-4"
        onMouseUp={handleTextSelect}
      >
        <div className="relative">
          <Document
            file={documentUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            loading={
              <div className="flex items-center justify-center p-12">
                <div className="text-muted-foreground">Loading PDF...</div>
              </div>
            }
            error={
              <div className="flex items-center justify-center p-12">
                <div className="text-destructive">Failed to load PDF</div>
              </div>
            }
          >
            <Page
              pageNumber={pageNumber}
              scale={scale}
              renderTextLayer={true}
              renderAnnotationLayer={true}
              className="shadow-lg"
            />
          </Document>

          {/* Annotation Markers */}
          {document.annotations
            ?.filter((ann) => ann.page_number === pageNumber)
            .map((annotation) => (
              <div
                key={annotation.id}
                className="absolute cursor-pointer"
                style={{
                  left: annotation.position?.x || 0,
                  top: annotation.position?.y || 0,
                  backgroundColor: annotation.color || '#ffeb3b',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  opacity: 0.7,
                }}
                title={annotation.content || ''}
                onClick={() => deleteAnnotation(annotation.id)}
              >
                {annotation.annotation_type === 'highlight' ? '📌' : '💬'}
              </div>
            ))}
        </div>
      </div>

      {/* Annotation Menu */}
      {showAnnotationMenu && (
        <Card
          className="fixed z-50 p-2 shadow-lg"
          style={{ left: menuPosition.x, top: menuPosition.y }}
        >
          <div className="flex flex-col gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="justify-start"
              onClick={() => createAnnotation('highlight', '#ffeb3b')}
            >
              📌 Highlight (Yellow)
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="justify-start"
              onClick={() => createAnnotation('highlight', '#4caf50')}
            >
              📌 Highlight (Green)
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="justify-start"
              onClick={() => createAnnotation('comment')}
            >
              💬 Add Comment
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="justify-start"
              onClick={() => createAnnotation('note')}
            >
              📝 Add Note
            </Button>
          </div>
        </Card>
      )}

      {/* Annotations Sidebar */}
      {document.annotations && document.annotations.length > 0 && (
        <Card className="mt-4 p-4">
          <h3 className="text-sm font-semibold mb-3">Annotations ({document.annotations.length})</h3>
          <div className="space-y-2 max-h-48 overflow-auto">
            {document.annotations.map((annotation) => (
              <div
                key={annotation.id}
                className="flex items-start gap-2 p-2 rounded-lg bg-muted/50 cursor-pointer hover:bg-muted"
                onClick={() => setPageNumber(annotation.page_number)}
              >
                <span className="text-lg">
                  {annotation.annotation_type === 'highlight' ? '📌' :
                   annotation.annotation_type === 'comment' ? '💬' : '📝'}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-muted-foreground">Page {annotation.page_number}</div>
                  <div className="text-sm truncate">{annotation.content}</div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteAnnotation(annotation.id);
                  }}
                >
                  ✕
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
