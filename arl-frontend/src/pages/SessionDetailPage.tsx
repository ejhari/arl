import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useSessionStore } from '@/stores/sessionStore';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  ArrowLeft,
  MessageSquare,
  Bot,
  Brain,
  FileText,
  Archive,
  Clock,
  Play,
  Plus,
} from 'lucide-react';
import type { SessionStatus, SessionMemory, SessionAgent } from '@/types/session';

const statusColors: Record<SessionStatus, string> = {
  active: 'bg-green-500',
  completed: 'bg-blue-500',
  archived: 'bg-gray-500',
  failed: 'bg-red-500',
};

const statusLabels: Record<SessionStatus, string> = {
  active: 'Active',
  completed: 'Completed',
  archived: 'Archived',
  failed: 'Failed',
};

export default function SessionDetailPage() {
  const { projectId, sessionId } = useParams<{ projectId: string; sessionId: string }>();
  const navigate = useNavigate();

  const {
    currentSession,
    sessionAgents,
    sessionMemories,
    isLoading,
    error,
    fetchSession,
    fetchSessionAgents,
    fetchSessionMemories,
    archiveSession,
    createSessionMemory,
  } = useSessionStore();

  const [showArchiveDialog, setShowArchiveDialog] = useState(false);
  const [newMemoryContent, setNewMemoryContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (projectId && sessionId) {
      fetchSession(projectId, sessionId);
      fetchSessionAgents(sessionId);
      fetchSessionMemories(sessionId);
    }
  }, [projectId, sessionId, fetchSession, fetchSessionAgents, fetchSessionMemories]);

  // Emit session name for breadcrumbs
  useEffect(() => {
    if (currentSession?.name) {
      window.dispatchEvent(
        new CustomEvent('session-loaded', { detail: { name: currentSession.name } })
      );
    }
  }, [currentSession?.name]);

  const handleArchive = async () => {
    if (!projectId || !sessionId) return;
    try {
      await archiveSession(projectId, sessionId, true);
      setShowArchiveDialog(false);
    } catch (err) {
      console.error('Failed to archive session:', err);
    }
  };

  const handleAddMemory = async () => {
    if (!sessionId || !projectId || !newMemoryContent.trim()) return;
    setIsSubmitting(true);
    try {
      await createSessionMemory(sessionId, {
        project_id: projectId,
        memory_type: 'insight',
        content: newMemoryContent.trim(),
      });
      setNewMemoryContent('');
    } catch (err) {
      console.error('Failed to add memory:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getMemoryTypeIcon = (type: string) => {
    switch (type) {
      case 'insight':
        return <Brain className="h-4 w-4" />;
      case 'artifact':
        return <FileText className="h-4 w-4" />;
      case 'decision':
        return <MessageSquare className="h-4 w-4" />;
      default:
        return <Brain className="h-4 w-4" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !currentSession) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <p className="text-destructive mb-4">{error || 'Session not found'}</p>
        <Button variant="outline" onClick={() => navigate(`/projects/${projectId}/sessions`)}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Sessions
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(`/projects/${projectId}/sessions`)}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <MessageSquare className="h-6 w-6 text-primary" />
              <h1 className="text-3xl font-bold tracking-tight">{currentSession.name}</h1>
              <Badge
                variant="outline"
                className={`${statusColors[currentSession.status]} text-white border-0`}
              >
                {statusLabels[currentSession.status]}
              </Badge>
            </div>
            {currentSession.description && (
              <p className="text-muted-foreground mt-2 ml-10">
                {currentSession.description}
              </p>
            )}
            <div className="flex items-center gap-4 mt-2 ml-10 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>Created {formatDate(currentSession.created_at)}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {currentSession.status === 'active' && (
            <>
              <Link to={`/canvas/${projectId}?session=${sessionId}`}>
                <Button>
                  <Play className="h-4 w-4 mr-2" />
                  Continue in Canvas
                </Button>
              </Link>
              <Button variant="outline" onClick={() => setShowArchiveDialog(true)}>
                <Archive className="h-4 w-4 mr-2" />
                Archive
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Initial Prompt */}
      {currentSession.initial_prompt && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Research Prompt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-muted p-4 rounded-lg">
              <p className="whitespace-pre-wrap">{currentSession.initial_prompt}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Session Memories</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sessionMemories.length}</div>
            <p className="text-xs text-muted-foreground">
              Insights and artifacts captured
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Enabled Agents</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sessionAgents.length}</div>
            <p className="text-xs text-muted-foreground">
              Agents enabled for this session
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Cells</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentSession.cell_count || 0}</div>
            <p className="text-xs text-muted-foreground">
              Notebook cells in session
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Memories Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Session Memories</CardTitle>
              <CardDescription>
                Captured insights, artifacts, and decisions from this research session
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Add Memory Form */}
          {currentSession.status === 'active' && (
            <div className="flex gap-2">
              <Textarea
                placeholder="Add a new insight or note..."
                value={newMemoryContent}
                onChange={(e) => setNewMemoryContent(e.target.value)}
                rows={2}
                className="flex-1"
              />
              <Button
                onClick={handleAddMemory}
                disabled={isSubmitting || !newMemoryContent.trim()}
              >
                {isSubmitting ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Add
                  </>
                )}
              </Button>
            </div>
          )}

          {/* Memory List */}
          {sessionMemories.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No memories captured yet. Start working in the canvas to generate insights.
            </div>
          ) : (
            <div className="space-y-3">
              {sessionMemories.map((memory: SessionMemory) => (
                <div
                  key={memory.id}
                  className="flex items-start gap-3 p-4 border rounded-lg"
                >
                  <div className="bg-primary/10 rounded-lg p-2">
                    {getMemoryTypeIcon(memory.memory_type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="capitalize">
                        {memory.memory_type}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(memory.created_at)}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{memory.content}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Enabled Agents */}
      <Card>
        <CardHeader>
          <CardTitle>Enabled Agents</CardTitle>
          <CardDescription>
            AI agents enabled for this session at time of creation
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sessionAgents.length === 0 ? (
            <div className="text-center py-4 text-muted-foreground">
              No agents were enabled when this session was created.
            </div>
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {sessionAgents.map((sa) => (
                <div
                  key={sa.id}
                  className="flex items-center gap-3 p-3 border rounded-lg"
                >
                  <Bot className="h-5 w-5 text-primary" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{sa.agent_display_name || sa.agent_name}</span>
                      {sa.is_system && (
                        <Badge variant="secondary" className="text-xs">System</Badge>
                      )}
                    </div>
                    {sa.agent_description && (
                      <p className="text-xs text-muted-foreground line-clamp-1">
                        {sa.agent_description}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Archive Dialog */}
      <Dialog open={showArchiveDialog} onOpenChange={setShowArchiveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Archive Session</DialogTitle>
            <DialogDescription>
              Archiving this session will generate a summary of insights and transfer
              them to project-level memories. You won't be able to continue working
              in this session after archiving.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowArchiveDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleArchive}>
              <Archive className="h-4 w-4 mr-2" />
              Archive Session
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
