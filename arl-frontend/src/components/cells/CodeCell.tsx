import { useState } from 'react';
import Editor from '@monaco-editor/react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import type { Cell, CellOutput } from '@/types/canvas';
import { canvasAPI } from '@/api/canvas';

interface CodeCellProps {
  cell: Cell;
  onUpdate: (cellId: string, content: string) => void;
  onDelete: (cellId: string) => void;
}

export function CodeCell({ cell, onUpdate, onDelete }: CodeCellProps) {
  const [code, setCode] = useState(cell.content || '');
  const [isExecuting, setIsExecuting] = useState(false);
  const [outputs, setOutputs] = useState<CellOutput[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleEditorChange = (value: string | undefined) => {
    const newCode = value || '';
    setCode(newCode);
  };

  const handleBlur = () => {
    if (code !== cell.content) {
      onUpdate(cell.id, code);
    }
  };

  const handleExecute = async () => {
    setIsExecuting(true);
    setError(null);
    setOutputs([]);

    try {
      const result = await canvasAPI.executeCell({
        cell_id: cell.id,
      });

      if (result.status === 'error') {
        setError(result.error || 'Execution failed');
      }

      setOutputs(result.outputs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleClearOutputs = () => {
    setOutputs([]);
    setError(null);
  };

  return (
    <Card className="mb-4">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-muted-foreground">
            Code Cell
          </span>
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={handleExecute}
              disabled={isExecuting || !code.trim()}
            >
              {isExecuting ? 'Running...' : 'Run'}
            </Button>
            {outputs.length > 0 && (
              <Button
                size="sm"
                variant="outline"
                onClick={handleClearOutputs}
              >
                Clear
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onDelete(cell.id)}
            >
              Delete
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="border rounded-md overflow-hidden">
          <Editor
            height="200px"
            defaultLanguage="python"
            value={code}
            onChange={handleEditorChange}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
            }}
            onMount={(editor) => {
              editor.onDidBlurEditorWidget(handleBlur);
            }}
          />
        </div>

        {/* Output Display */}
        {(outputs.length > 0 || error) && (
          <div className="mt-4 space-y-2">
            {error && (
              <div className="rounded-md bg-destructive/15 p-3 text-sm text-destructive">
                <pre className="whitespace-pre-wrap font-mono">{error}</pre>
              </div>
            )}

            {outputs.map((output) => (
              <div
                key={output.id}
                className={`rounded-md p-3 text-sm font-mono ${
                  output.output_type === 'stderr' || output.output_type === 'error'
                    ? 'bg-destructive/15 text-destructive'
                    : output.output_type === 'result'
                    ? 'bg-primary/15 text-primary'
                    : 'bg-muted text-foreground'
                }`}
              >
                <pre className="whitespace-pre-wrap">{output.content}</pre>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
