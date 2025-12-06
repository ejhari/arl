import { useState, useEffect, useRef, useCallback } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import type { Annotation } from '@/types/document';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Highlighter, StickyNote, Loader2, AlertCircle, MessageSquare } from 'lucide-react';
import { Input } from '@/components/ui/input';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// PDF.js types - using 'any' to avoid pdfjs-dist type compatibility issues
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type PDFDocumentProxy = any;

// Custom styles for text selection in PDF
const pdfStyles = `
  /* Ensure the text layer is above canvas and clickable */
  .pdf-viewer-container .react-pdf__Page {
    position: relative !important;
  }

  .pdf-viewer-container .react-pdf__Page__canvas {
    display: block;
    user-select: none;
  }

  /* Text layer must be above canvas with proper z-index */
  .pdf-viewer-container .react-pdf__Page__textContent,
  .pdf-viewer-container .textLayer {
    position: absolute !important;
    left: 0;
    top: 0;
    right: 0;
    bottom: 0;
    overflow: hidden;
    line-height: 1;
    z-index: 2 !important;
    user-select: text !important;
    cursor: text !important;
    pointer-events: auto !important;
  }

  /* Make text spans selectable */
  .pdf-viewer-container .react-pdf__Page__textContent span,
  .pdf-viewer-container .textLayer span {
    color: transparent;
    position: absolute;
    white-space: pre;
    cursor: text !important;
    user-select: text !important;
    pointer-events: auto !important;
  }

  /* Selection highlight color */
  .pdf-viewer-container .react-pdf__Page__textContent span::selection,
  .pdf-viewer-container .textLayer span::selection {
    background: rgba(0, 100, 255, 0.4) !important;
    color: transparent !important;
  }

  /* Annotation layer should not block text selection */
  .pdf-viewer-container .react-pdf__Page__annotations,
  .pdf-viewer-container .annotationLayer {
    pointer-events: none;
  }

  /* But allow clicks on actual annotations */
  .pdf-viewer-container .react-pdf__Page__annotations > *,
  .pdf-viewer-container .annotationLayer > * {
    pointer-events: auto;
  }
`;

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface StoredSelection {
  text: string;
  // Position relative to PDF page container, normalized to scale 1.0
  relativeX: number;
  relativeY: number;
  width: number;
  height: number;
}

// Comment color - violet/purple, distinct from highlight colors
const COMMENT_COLOR = 'rgba(167, 139, 250, 0.4)'; // violet-400 with transparency

interface PDFViewerProps {
  documentId: string;
  fileUrl: string;
  annotations: Annotation[];
  onAnnotationCreate: (annotation: Omit<Annotation, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => void;
  /** Callback when an annotation is updated (e.g., adding a reply) */
  onAnnotationUpdate?: (annotationId: string, data: { content?: string }) => Promise<void>;
  /** Current page to display (controlled) */
  currentPage?: number;
  /** Callback when page changes */
  onPageChange?: (page: number) => void;
}

export function PDFViewer({ documentId, fileUrl, annotations, onAnnotationCreate, onAnnotationUpdate, currentPage, onPageChange }: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [internalPageNumber, setInternalPageNumber] = useState<number>(1);

  // Use controlled page if provided, otherwise use internal state
  const pageNumber = currentPage ?? internalPageNumber;
  const setPageNumber = useCallback((page: number | ((prev: number) => number)) => {
    const newPage = typeof page === 'function' ? page(pageNumber) : page;
    setInternalPageNumber(newPage);
    onPageChange?.(newPage);
  }, [pageNumber, onPageChange]);

  const [scale, setScale] = useState<number>(1.0);
  const [selectedColor, setSelectedColor] = useState<string>('yellow');
  const [storedSelection, setStoredSelection] = useState<StoredSelection | null>(null);
  const [noteDialogOpen, setNoteDialogOpen] = useState(false);
  const [noteContent, setNoteContent] = useState('');
  const [commentDialogOpen, setCommentDialogOpen] = useState(false);
  const [commentContent, setCommentContent] = useState('');
  const [threadDialogOpen, setThreadDialogOpen] = useState(false);
  const [selectedAnnotation, setSelectedAnnotation] = useState<Annotation | null>(null);
  const [replyContent, setReplyContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [hasTextContent, setHasTextContent] = useState<boolean>(true);
  const [pageTextLoading, setPageTextLoading] = useState<boolean>(true);
  const [pageInputValue, setPageInputValue] = useState<string>('1');
  const pdfContainerRef = useRef<HTMLDivElement>(null);
  const pdfPageRef = useRef<HTMLDivElement>(null);
  const pdfDocRef = useRef<PDFDocumentProxy | null>(null);
  const pageRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  // Listen for text selection within the PDF container
  useEffect(() => {
    const handleMouseUp = () => {
      const selection = window.getSelection();
      if (!selection || selection.toString().trim() === '') {
        return;
      }

      // Check if selection is within the PDF container
      if (pdfContainerRef.current && pdfPageRef.current) {
        const range = selection.getRangeAt(0);
        if (pdfContainerRef.current.contains(range.commonAncestorContainer)) {
          const selectionRect = range.getBoundingClientRect();

          // Get the PDF page container's bounding rect
          const pageRect = pdfPageRef.current.getBoundingClientRect();

          // Calculate position relative to PDF page container
          // Normalize to scale 1.0 by dividing by current scale
          const relativeX = (selectionRect.x - pageRect.x) / scale;
          const relativeY = (selectionRect.y - pageRect.y) / scale;

          setStoredSelection({
            text: selection.toString(),
            relativeX,
            relativeY,
            width: selectionRect.width / scale,
            height: selectionRect.height / scale,
          });
        }
      }
    };

    document.addEventListener('mouseup', handleMouseUp);
    return () => document.removeEventListener('mouseup', handleMouseUp);
  }, [scale]);

  const onDocumentLoadSuccess = (pdf: PDFDocumentProxy) => {
    pdfDocRef.current = pdf;
    setNumPages(pdf.numPages);
    setIsLoading(false);
    setLoadError(null);
    // Check text content for first page
    checkPageTextContent(1, pdf);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('PDF load error:', error);
    setLoadError('Failed to load PDF document');
    setIsLoading(false);
  };

  // Check if a page has text content (not just an image/scanned PDF)
  const checkPageTextContent = async (pageNum: number, pdf?: PDFDocumentProxy) => {
    const pdfDoc = pdf || pdfDocRef.current;
    if (!pdfDoc) return;

    setPageTextLoading(true);
    try {
      const page = await pdfDoc.getPage(pageNum);
      const textContent = await page.getTextContent();

      // Check if there are any text items
      const hasText = textContent.items.length > 0 &&
        textContent.items.some((item: { str?: string }) =>
          'str' in item && item.str && item.str.trim().length > 0
        );

      setHasTextContent(hasText);

      if (!hasText) {
        console.log(`Page ${pageNum} has no selectable text (likely a scanned/image PDF)`);
      }
    } catch (error) {
      console.error('Error checking text content:', error);
      setHasTextContent(false);
    } finally {
      setPageTextLoading(false);
    }
  };

  // Sync internal page number when controlled prop changes (e.g., from sidebar click)
  useEffect(() => {
    if (currentPage !== undefined && currentPage !== internalPageNumber) {
      setInternalPageNumber(currentPage);
      setPageInputValue(String(currentPage));
      setStoredSelection(null);
      checkPageTextContent(currentPage);
      // Scroll to the page
      scrollToPage(currentPage);
    }
  }, [currentPage, internalPageNumber]);

  // Sync page input value when page number changes internally
  useEffect(() => {
    setPageInputValue(String(pageNumber));
  }, [pageNumber]);

  // Scroll to a specific page
  const scrollToPage = (page: number) => {
    const pageElement = pageRefs.current.get(page);
    if (pageElement) {
      pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // Set up intersection observer for page tracking
  useEffect(() => {
    if (!numPages || isLoading) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
            const pageNum = parseInt(entry.target.getAttribute('data-page-number') || '1', 10);
            if (pageNum !== pageNumber) {
              setInternalPageNumber(pageNum);
              onPageChange?.(pageNum);
            }
          }
        });
      },
      {
        root: pdfContainerRef.current,
        threshold: 0.5,
      }
    );

    // Observe all page elements
    pageRefs.current.forEach((element) => {
      observer.observe(element);
    });

    return () => observer.disconnect();
  }, [numPages, isLoading, pageNumber, onPageChange]);

  const handlePreviousPage = () => {
    const newPage = Math.max(pageNumber - 1, 1);
    setPageNumber(newPage);
    setStoredSelection(null);
    checkPageTextContent(newPage);
    scrollToPage(newPage);
  };

  const handleNextPage = () => {
    const newPage = Math.min(pageNumber + 1, numPages);
    setPageNumber(newPage);
    setStoredSelection(null);
    checkPageTextContent(newPage);
    scrollToPage(newPage);
  };

  const handlePageInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPageInputValue(e.target.value);
  };

  const handlePageInputSubmit = (e: React.FormEvent | React.FocusEvent) => {
    e.preventDefault();
    const newPage = parseInt(pageInputValue, 10);
    if (!isNaN(newPage) && newPage >= 1 && newPage <= numPages) {
      setPageNumber(newPage);
      setStoredSelection(null);
      checkPageTextContent(newPage);
      scrollToPage(newPage);
    } else {
      // Reset to current page if invalid
      setPageInputValue(String(pageNumber));
    }
  };

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.2, 2.0));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.2, 0.5));
  };

  const handleHighlightSelection = useCallback(() => {
    if (!storedSelection) return;

    // Create highlight annotation with coordinates relative to PDF page
    onAnnotationCreate({
      document_id: documentId,
      annotation_type: 'highlight',
      page_number: pageNumber,
      content: storedSelection.text,
      color: selectedColor,
      position: {
        x: storedSelection.relativeX,
        y: storedSelection.relativeY,
        width: storedSelection.width,
        height: storedSelection.height,
      },
    });

    // Clear selection
    window.getSelection()?.removeAllRanges();
    setStoredSelection(null);
  }, [storedSelection, documentId, pageNumber, selectedColor, onAnnotationCreate]);

  const handleOpenNoteDialog = () => {
    setNoteContent('');
    setNoteDialogOpen(true);
  };

  const handleAddNote = () => {
    if (!noteContent.trim()) return;

    onAnnotationCreate({
      document_id: documentId,
      annotation_type: 'note',
      page_number: pageNumber,
      content: noteContent.trim(),
      color: null,
      position: null,
    });

    setNoteContent('');
    setNoteDialogOpen(false);
  };

  const handleOpenCommentDialog = () => {
    if (!storedSelection) return;
    setCommentContent('');
    setCommentDialogOpen(true);
  };

  const handleAddComment = () => {
    if (!commentContent.trim() || !storedSelection) return;

    // Create comment with the selected text and user's comment
    onAnnotationCreate({
      document_id: documentId,
      annotation_type: 'comment',
      page_number: pageNumber,
      content: `"${storedSelection.text}"\n\n${commentContent.trim()}`,
      color: selectedColor,
      position: {
        x: storedSelection.relativeX,
        y: storedSelection.relativeY,
        width: storedSelection.width,
        height: storedSelection.height,
      },
    });

    // Clear selection and dialog
    window.getSelection()?.removeAllRanges();
    setStoredSelection(null);
    setCommentContent('');
    setCommentDialogOpen(false);
  };

  const colorOptions = [
    { name: 'Yellow', value: 'yellow', class: 'bg-yellow-300' },
    { name: 'Green', value: 'green', class: 'bg-green-300' },
    { name: 'Blue', value: 'blue', class: 'bg-blue-300' },
    { name: 'Pink', value: 'pink', class: 'bg-pink-300' },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Inject PDF styles for text selection */}
      <style dangerouslySetInnerHTML={{ __html: pdfStyles }} />

      {/* Toolbar - Responsive layout */}
      <div className="bg-background border-b p-2 flex flex-wrap items-center gap-2">
        {/* Left side: Page Navigation */}
        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={handlePreviousPage}
            disabled={pageNumber <= 1 || isLoading}
            title="Previous page"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <form onSubmit={handlePageInputSubmit} className="flex items-center gap-1">
            <Input
              type="text"
              value={pageInputValue}
              onChange={handlePageInputChange}
              onBlur={handlePageInputSubmit}
              className="h-8 w-12 text-center text-sm px-1"
              disabled={isLoading}
            />
            <span className="text-sm text-muted-foreground">/ {numPages || '?'}</span>
          </form>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={handleNextPage}
            disabled={pageNumber >= numPages || isLoading}
            title="Next page"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        <div className="w-px h-6 bg-border hidden sm:block" />

        {/* Zoom Controls */}
        <div className="flex items-center gap-1">
          <Button variant="outline" size="icon" className="h-8 w-8" onClick={handleZoomOut} title="Zoom out">
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm min-w-[3rem] text-center">{Math.round(scale * 100)}%</span>
          <Button variant="outline" size="icon" className="h-8 w-8" onClick={handleZoomIn} title="Zoom in">
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>

        {/* Spacer to push right-aligned items */}
        <div className="flex-1" />

        {/* Right side: Color Selection */}
        <div className="flex items-center gap-1">
          {colorOptions.map((color) => (
            <button
              key={color.value}
              className={`w-6 h-6 rounded-full ${color.class} transition-all ${
                selectedColor === color.value
                  ? 'ring-2 ring-primary ring-offset-2 ring-offset-background'
                  : 'hover:ring-1 hover:ring-muted-foreground'
              }`}
              onClick={() => setSelectedColor(color.value)}
              title={color.name}
            />
          ))}
        </div>

        <div className="w-px h-6 bg-border" />

        {/* Action Buttons */}
        <div className="flex items-center gap-1">
          <Button
            variant={storedSelection ? 'default' : 'outline'}
            size="sm"
            className="h-8 gap-1.5"
            onClick={handleHighlightSelection}
            disabled={!storedSelection || !hasTextContent}
            title={
              !hasTextContent
                ? 'Text selection not available (scanned/image PDF)'
                : storedSelection
                ? `Highlight: "${storedSelection.text.substring(0, 20)}..."`
                : 'Select text to highlight'
            }
          >
            <Highlighter className="h-4 w-4" />
            <span className="hidden md:inline">Highlight</span>
          </Button>
          <Button
            variant={storedSelection ? 'default' : 'outline'}
            size="sm"
            className="h-8 gap-1.5"
            onClick={handleOpenCommentDialog}
            disabled={!storedSelection || !hasTextContent}
            title={
              !hasTextContent
                ? 'Text selection not available (scanned/image PDF)'
                : storedSelection
                ? `Comment on: "${storedSelection.text.substring(0, 20)}..."`
                : 'Select text to comment'
            }
          >
            <MessageSquare className="h-4 w-4" />
            <span className="hidden md:inline">Comment</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-8 gap-1.5"
            onClick={handleOpenNoteDialog}
            title="Add a note to this page"
          >
            <StickyNote className="h-4 w-4" />
            <span className="hidden md:inline">Note</span>
          </Button>
        </div>

        {/* Text availability indicator */}
        {!pageTextLoading && !hasTextContent && (
          <div className="flex items-center gap-1 text-amber-600 dark:text-amber-500" title="This page appears to be a scanned image without selectable text">
            <AlertCircle className="h-4 w-4" />
            <span className="text-xs hidden lg:inline">No selectable text</span>
          </div>
        )}
      </div>

      {/* PDF Document */}
      <div
        ref={pdfContainerRef}
        className="flex-1 overflow-auto p-4 flex flex-col items-center pdf-viewer-container"
      >
        {/* No text content banner */}
        {!isLoading && !loadError && !hasTextContent && !pageTextLoading && (
          <div className="mb-4 px-4 py-2 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-lg flex items-center gap-2 text-amber-800 dark:text-amber-200 text-sm">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>
              This page appears to be a scanned image. Text selection and highlighting are not available.
              You can still add notes to this page.
            </span>
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        )}

        {/* Error state */}
        {loadError && (
          <div className="flex items-center justify-center h-full text-destructive">
            {loadError}
          </div>
        )}

        <div ref={pdfPageRef} style={{ display: isLoading || loadError ? 'none' : 'block' }}>
          <Document
            file={fileUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading=""
          >
            {/* Render all pages for vertical scrolling */}
            {Array.from({ length: numPages }, (_, index) => {
              const pageNum = index + 1;
              const pageAnnotationsForPage = annotations.filter((a) => a.page_number === pageNum);

              return (
                <div
                  key={pageNum}
                  ref={(el) => {
                    if (el) pageRefs.current.set(pageNum, el);
                  }}
                  data-page-number={pageNum}
                  className="relative mb-4"
                >
                  <Page
                    pageNumber={pageNum}
                    scale={scale}
                    renderTextLayer={true}
                    renderAnnotationLayer={true}
                    className="pdf-page shadow-lg"
                  />

                  {/* Render highlights for this page */}
                  {pageAnnotationsForPage
                    .filter((a) => a.annotation_type === 'highlight' && a.position)
                    .map((annotation) => (
                      <div
                        key={annotation.id}
                        className="absolute pointer-events-none"
                        style={{
                          left: `${(annotation.position?.x || 0) * scale}px`,
                          top: `${(annotation.position?.y || 0) * scale}px`,
                          width: `${(annotation.position?.width || 0) * scale}px`,
                          height: `${(annotation.position?.height || 0) * scale}px`,
                          backgroundColor:
                            annotation.color === 'yellow'
                              ? 'rgba(253, 224, 71, 0.4)'
                              : annotation.color === 'green'
                              ? 'rgba(134, 239, 172, 0.4)'
                              : annotation.color === 'blue'
                              ? 'rgba(147, 197, 253, 0.4)'
                              : 'rgba(249, 168, 212, 0.4)',
                        }}
                      />
                    ))}

                  {/* Render comments with violet color and clickable icon */}
                  {pageAnnotationsForPage
                    .filter((a) => a.annotation_type === 'comment' && a.position)
                    .map((annotation) => (
                      <div key={annotation.id}>
                        {/* Highlight overlay */}
                        <div
                          className="absolute pointer-events-none"
                          style={{
                            left: `${(annotation.position?.x || 0) * scale}px`,
                            top: `${(annotation.position?.y || 0) * scale}px`,
                            width: `${(annotation.position?.width || 0) * scale}px`,
                            height: `${(annotation.position?.height || 0) * scale}px`,
                            backgroundColor: COMMENT_COLOR,
                          }}
                        />
                        {/* Clickable comment icon */}
                        <button
                          className="absolute flex items-center justify-center w-5 h-5 rounded-full bg-violet-500 text-white shadow-md hover:bg-violet-600 transition-colors cursor-pointer z-10"
                          style={{
                            left: `${((annotation.position?.x || 0) + (annotation.position?.width || 0)) * scale + 4}px`,
                            top: `${(annotation.position?.y || 0) * scale}px`,
                          }}
                          onClick={() => {
                            setSelectedAnnotation(annotation);
                            setThreadDialogOpen(true);
                          }}
                          title="View comment thread"
                        >
                          <MessageSquare className="h-3 w-3" />
                        </button>
                      </div>
                    ))}
                </div>
              );
            })}
          </Document>
        </div>
      </div>

      {/* Add Note Dialog */}
      <Dialog open={noteDialogOpen} onOpenChange={setNoteDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add Note</DialogTitle>
            <DialogDescription>
              Add a note to page {pageNumber} of this document.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <textarea
              value={noteContent}
              onChange={(e) => setNoteContent(e.target.value)}
              placeholder="Enter your note..."
              className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setNoteDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddNote} disabled={!noteContent.trim()}>
              Add Note
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Comment Dialog */}
      <Dialog open={commentDialogOpen} onOpenChange={setCommentDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add Comment</DialogTitle>
            <DialogDescription>
              Comment on the selected text on page {pageNumber}.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-3">
            {storedSelection && (
              <div className="p-2 bg-violet-100 dark:bg-violet-950 border border-violet-200 dark:border-violet-800 rounded text-sm">
                <span className="text-violet-700 dark:text-violet-300 italic">
                  "{storedSelection.text.length > 100
                    ? storedSelection.text.substring(0, 100) + '...'
                    : storedSelection.text}"
                </span>
              </div>
            )}
            <textarea
              value={commentContent}
              onChange={(e) => setCommentContent(e.target.value)}
              placeholder="Enter your comment..."
              className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCommentDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddComment} disabled={!commentContent.trim()}>
              Add Comment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Comment Thread Dialog */}
      <Dialog open={threadDialogOpen} onOpenChange={(open) => {
        setThreadDialogOpen(open);
        if (!open) {
          setSelectedAnnotation(null);
          setReplyContent('');
        }
      }}>
        <DialogContent className="sm:max-w-lg max-h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-violet-500" />
              Comment Thread
            </DialogTitle>
            <DialogDescription>
              Page {selectedAnnotation?.page_number}
            </DialogDescription>
          </DialogHeader>

          {selectedAnnotation && (
            <div className="flex-1 overflow-auto py-4 space-y-4">
              {/* Parse and display the comment content */}
              {(() => {
                const content = selectedAnnotation.content || '';
                // Split by double newline to separate quoted text from comments
                const parts = content.split('\n\n');
                const quotedText = parts[0]?.replace(/^"|"$/g, '') || '';
                const comments = parts.slice(1);

                return (
                  <>
                    {/* Quoted text */}
                    {quotedText && (
                      <div className="p-3 bg-violet-50 dark:bg-violet-950 border-l-4 border-violet-400 rounded-r">
                        <p className="text-sm text-violet-700 dark:text-violet-300 italic">
                          "{quotedText}"
                        </p>
                      </div>
                    )}

                    {/* Main comment and replies - displayed at same level */}
                    {comments.length > 0 && (
                      <div className="space-y-3">
                        {comments.map((comment, index) => {
                          // Check if it's a reply (starts with "Reply:")
                          const isReply = comment.startsWith('Reply:');
                          const displayText = isReply ? comment.substring(6).trim() : comment;

                          return (
                            <div
                              key={index}
                              className="p-3 rounded-lg bg-card border"
                            >
                              <p className="text-sm whitespace-pre-wrap">{displayText}</p>
                              <p className="text-xs text-muted-foreground mt-2">
                                {isReply ? 'Reply' : 'Comment'} • {new Date(selectedAnnotation.created_at).toLocaleString()}
                              </p>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* Reply input */}
                    <div className="pt-4 border-t">
                      <textarea
                        value={replyContent}
                        onChange={(e) => setReplyContent(e.target.value)}
                        placeholder="Write a reply..."
                        className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 resize-none"
                      />
                      <div className="flex justify-end mt-2">
                        <Button
                          size="sm"
                          disabled={!replyContent.trim() || !onAnnotationUpdate}
                          onClick={async () => {
                            if (!selectedAnnotation || !replyContent.trim() || !onAnnotationUpdate) return;
                            const newContent = `${selectedAnnotation.content}\n\nReply:${replyContent.trim()}`;
                            try {
                              await onAnnotationUpdate(selectedAnnotation.id, { content: newContent });
                              setReplyContent('');
                              // Update local state to show the reply immediately
                              setSelectedAnnotation({
                                ...selectedAnnotation,
                                content: newContent,
                              });
                            } catch (error) {
                              console.error('Failed to add reply:', error);
                            }
                          }}
                        >
                          Reply
                        </Button>
                      </div>
                    </div>
                  </>
                );
              })()}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
