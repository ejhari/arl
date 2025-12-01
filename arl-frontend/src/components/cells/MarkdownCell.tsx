import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import type { Cell } from '@/types/canvas';

interface MarkdownCellProps {
  cell: Cell;
  onUpdate: (cellId: string, content: string) => void;
  onDelete: (cellId: string) => void;
}

export function MarkdownCell({ cell, onUpdate, onDelete }: MarkdownCellProps) {
  const [content, setContent] = useState(cell.content || '');
  const [isEditing, setIsEditing] = useState(!cell.content);

  const handleSave = () => {
    onUpdate(cell.id, content);
    setIsEditing(false);
  };

  return (
    <Card className="mb-4">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-muted-foreground">
            Markdown Cell
          </span>
          <div className="flex gap-2">
            {isEditing ? (
              <Button size="sm" onClick={handleSave}>
                Save
              </Button>
            ) : (
              <Button size="sm" variant="outline" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
            )}
            <Button size="sm" variant="ghost" onClick={() => onDelete(cell.id)}>
              Delete
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isEditing ? (
          <textarea
            className="w-full min-h-[100px] p-3 rounded-md border bg-background font-mono text-sm"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter markdown content..."
          />
        ) : (
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap">{content}</pre>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
