import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCanvasStore } from '@/stores/canvasStore';
import { useWebSocketStore } from '@/stores/websocketStore';
import { CodeCell } from '@/components/cells/CodeCell';
import { MarkdownCell } from '@/components/cells/MarkdownCell';
import { VisualizationCell } from '@/components/cells/VisualizationCell';
import { ExportDialog } from '@/components/export/ExportDialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Download } from 'lucide-react';
import type { CellType } from '@/types/canvas';
import { EventType } from '@/types/events';

export function CanvasPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const {
    currentProject,
    cells,
    loadProject,
    createCell,
    updateCell,
    deleteCell,
    updateCellLocal,
    removeCellLocal,
    error,
  } = useCanvasStore();

  const [isCreatingCell, setIsCreatingCell] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);

  // Load project and cells
  useEffect(() => {
    if (projectId) {
      loadProject(projectId);
    }
  }, [projectId]);

  // Subscribe to real-time cell events
  useEffect(() => {
    const unsubscribe = useWebSocketStore.subscribe((state) => {
      const latestEvent = state.events[state.events.length - 1];
      if (!latestEvent || !projectId) return;

      // Only handle events for this project
      const eventData = latestEvent.data as any;
      if (eventData.project_id !== projectId) return;

      switch (latestEvent.type) {
        case EventType.CELL_CREATED:
          // Cell will be added via API response, but we can show notification
          console.log('Cell created:', eventData.cell_id);
          break;

        case EventType.CELL_UPDATED:
          updateCellLocal(eventData.cell_id, {
            content: eventData.content,
            position: eventData.position,
          });
          break;

        case EventType.CELL_DELETED:
          removeCellLocal(eventData.cell_id);
          break;

        case EventType.CELL_EXECUTED:
          console.log('Cell executed:', eventData.cell_id);
          break;
      }
    });

    return unsubscribe;
  }, [projectId, updateCellLocal, removeCellLocal]);

  const handleCreateCell = async (cellType: CellType) => {
    if (!projectId) return;

    setIsCreatingCell(true);
    try {
      await createCell({
        project_id: projectId,
        cell_type: cellType,
        content: '',
        position: cells.length,
      });
    } catch (err) {
      console.error('Failed to create cell:', err);
    } finally {
      setIsCreatingCell(false);
    }
  };

  const handleUpdateCell = async (cellId: string, content: string) => {
    try {
      await updateCell(cellId, { content });
    } catch (err) {
      console.error('Failed to update cell:', err);
    }
  };

  const handleDeleteCell = async (cellId: string) => {
    if (!confirm('Are you sure you want to delete this cell?')) return;

    try {
      await deleteCell(cellId);
    } catch (err) {
      console.error('Failed to delete cell:', err);
    }
  };

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">Loading project...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Project Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{currentProject.name}</h1>
          {currentProject.description && (
            <p className="text-muted-foreground mt-1">{currentProject.description}</p>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowExportDialog(true)}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" onClick={() => navigate(`/documents/${projectId}`)}>
            <FileText className="h-4 w-4 mr-2" />
            Documents
          </Button>
          <Button variant="outline" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="rounded-md bg-destructive/15 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Cells */}
      <div className="space-y-4">
        {cells.map((cell) => {
          switch (cell.cell_type) {
            case 'code':
              return (
                <CodeCell
                  key={cell.id}
                  cell={cell}
                  onUpdate={handleUpdateCell}
                  onDelete={handleDeleteCell}
                />
              );
            case 'markdown':
              return (
                <MarkdownCell
                  key={cell.id}
                  cell={cell}
                  onUpdate={handleUpdateCell}
                  onDelete={handleDeleteCell}
                />
              );
            case 'visualization':
              return (
                <VisualizationCell
                  key={cell.id}
                  cell={cell}
                  onUpdate={handleUpdateCell}
                  onDelete={handleDeleteCell}
                />
              );
            default:
              return (
                <Card key={cell.id} className="mb-4">
                  <CardContent className="p-4">
                    <p className="text-sm text-muted-foreground">
                      Unsupported cell type: {cell.cell_type}
                    </p>
                  </CardContent>
                </Card>
              );
          }
        })}
      </div>

      {/* Add Cell Actions */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Button
              onClick={() => handleCreateCell('code')}
              disabled={isCreatingCell}
            >
              + Code Cell
            </Button>
            <Button
              variant="outline"
              onClick={() => handleCreateCell('markdown')}
              disabled={isCreatingCell}
            >
              + Markdown Cell
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                // Create a sample visualization cell
                if (!projectId) return;
                setIsCreatingCell(true);
                const sampleData = JSON.stringify({
                  type: 'bar',
                  library: 'recharts',
                  title: 'Sample Bar Chart',
                  data: [
                    { name: 'A', value: 400 },
                    { name: 'B', value: 300 },
                    { name: 'C', value: 500 },
                    { name: 'D', value: 200 },
                  ],
                  xKey: 'name',
                  yKey: 'value',
                });
                createCell({
                  project_id: projectId,
                  cell_type: 'visualization',
                  content: sampleData,
                  position: cells.length,
                }).finally(() => setIsCreatingCell(false));
              }}
              disabled={isCreatingCell}
            >
              + Visualization Cell
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Export Dialog */}
      {showExportDialog && projectId && (
        <ExportDialog projectId={projectId} onClose={() => setShowExportDialog(false)} />
      )}
    </div>
  );
}
