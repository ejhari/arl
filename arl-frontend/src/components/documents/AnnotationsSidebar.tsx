import type { Annotation } from '@/types/document';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Trash2, MessageSquare, StickyNote, Highlighter } from 'lucide-react';

interface AnnotationsSidebarProps {
  annotations: Annotation[];
  onAnnotationDelete: (annotationId: string) => void;
  /** Callback when an annotation is clicked - navigates to that page */
  onAnnotationClick?: (annotation: Annotation) => void;
}

// Format date to human readable format
const formatDateTime = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    hour: '2-digit',
    minute: '2-digit',
  });
};

export function AnnotationsSidebar({ annotations, onAnnotationDelete, onAnnotationClick }: AnnotationsSidebarProps) {
  const highlights = annotations.filter((a) => a.annotation_type === 'highlight');
  const comments = annotations.filter((a) => a.annotation_type === 'comment');
  const notes = annotations.filter((a) => a.annotation_type === 'note');

  const getHighlightIconColor = (color: string | null) => {
    switch (color) {
      case 'yellow':
        return 'text-yellow-500';
      case 'green':
        return 'text-green-500';
      case 'blue':
        return 'text-blue-500';
      case 'pink':
        return 'text-pink-500';
      default:
        return 'text-gray-500';
    }
  };

  const renderAnnotation = (annotation: Annotation) => (
    <div
      key={annotation.id}
      className="mb-3 p-3 rounded-md border bg-card cursor-pointer hover:bg-accent/50 transition-colors"
      onClick={() => onAnnotationClick?.(annotation)}
    >
      {/* Header row */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5">
          {annotation.annotation_type === 'highlight' && (
            <Highlighter className={`h-3 w-3 flex-shrink-0 ${getHighlightIconColor(annotation.color)}`} />
          )}
          {annotation.annotation_type === 'comment' && (
            <MessageSquare className="h-3 w-3 text-violet-500 flex-shrink-0" />
          )}
          {annotation.annotation_type === 'note' && (
            <StickyNote className="h-3 w-3 text-amber-500 flex-shrink-0" />
          )}
          <span className="text-xs text-muted-foreground">Page {annotation.page_number}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 flex-shrink-0"
          onClick={(e) => {
            e.stopPropagation();
            if (confirm('Delete this annotation?')) {
              onAnnotationDelete(annotation.id);
            }
          }}
        >
          <Trash2 className="h-3 w-3 text-destructive" />
        </Button>
      </div>

      {/* Content */}
      {annotation.content && (
        <p className="text-sm text-foreground whitespace-pre-wrap break-words mb-2">
          {annotation.annotation_type === 'comment'
            ? (() => {
                // For comments, extract only the original comment (exclude replies)
                const parts = annotation.content.split('\n\n');
                // parts[0] is quoted text, parts[1] is original comment
                return parts.slice(0, 2).join('\n\n');
              })()
            : annotation.content
          }
        </p>
      )}

      {/* Timestamp */}
      <p className="text-xs text-muted-foreground">
        {formatDateTime(annotation.created_at)}
      </p>
    </div>
  );

  return (
    <div className="w-80 border-l bg-background overflow-auto">
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4">Annotations</h2>

        <Tabs defaultValue="all" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all" className="text-xs">
              All
              <span className="ml-1 text-xs">({annotations.length})</span>
            </TabsTrigger>
            <TabsTrigger value="highlights" className="text-xs">
              <Highlighter className="h-3 w-3" />
              <span className="ml-1">({highlights.length})</span>
            </TabsTrigger>
            <TabsTrigger value="comments" className="text-xs">
              <MessageSquare className="h-3 w-3" />
              <span className="ml-1">({comments.length})</span>
            </TabsTrigger>
            <TabsTrigger value="notes" className="text-xs">
              <StickyNote className="h-3 w-3" />
              <span className="ml-1">({notes.length})</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-4">
            {annotations.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-sm text-muted-foreground">No annotations yet</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Select text to highlight or add notes
                </p>
              </div>
            ) : (
              <div>
                {annotations
                  .sort((a, b) => b.page_number - a.page_number || new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                  .map(renderAnnotation)}
              </div>
            )}
          </TabsContent>

          <TabsContent value="highlights" className="mt-4">
            {highlights.length === 0 ? (
              <div className="text-center py-8">
                <Highlighter className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">No highlights yet</p>
              </div>
            ) : (
              <div>{highlights.map(renderAnnotation)}</div>
            )}
          </TabsContent>

          <TabsContent value="comments" className="mt-4">
            {comments.length === 0 ? (
              <div className="text-center py-8">
                <MessageSquare className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">No comments yet</p>
              </div>
            ) : (
              <div>{comments.map(renderAnnotation)}</div>
            )}
          </TabsContent>

          <TabsContent value="notes" className="mt-4">
            {notes.length === 0 ? (
              <div className="text-center py-8">
                <StickyNote className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">No notes yet</p>
              </div>
            ) : (
              <div>{notes.map(renderAnnotation)}</div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
