import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSessionStore } from '@/stores/sessionStore';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  MessageSquare,
  Plus,
  Archive,
  Trash2,
  MoreVertical,
  Clock,
  Brain,
  FileText,
  Play,
} from 'lucide-react';
import type { Session, CreateSessionData, SessionStatus } from '@/types/session';

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

export default function SessionsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const {
    sessions,
    isLoading,
    error,
    fetchSessions,
    createSession,
    archiveSession,
    deleteSession,
  } = useSessionStore();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'active' | 'archived'>('all');
  const [formData, setFormData] = useState<CreateSessionData>({
    name: '',
    description: '',
    initial_prompt: '',
  });

  useEffect(() => {
    if (projectId) {
      const statusFilter = activeTab === 'all' ? undefined : activeTab;
      fetchSessions(projectId, statusFilter);
    }
  }, [projectId, activeTab, fetchSessions]);

  const handleCreateSession = async () => {
    if (!projectId) return;
    try {
      const session = await createSession(projectId, formData);
      setIsCreateDialogOpen(false);
      resetForm();
      // Navigate to the new session
      navigate(`/projects/${projectId}/sessions/${session.id}`);
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleArchiveSession = async (sessionId: string) => {
    if (!projectId) return;
    if (confirm('Are you sure you want to archive this session? This action cannot be undone.')) {
      try {
        await archiveSession(projectId, sessionId);
      } catch (err) {
        console.error('Failed to archive session:', err);
      }
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    if (!projectId) return;
    if (confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
      try {
        await deleteSession(projectId, sessionId);
      } catch (err) {
        console.error('Failed to delete session:', err);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      initial_prompt: '',
    });
  };

  const filteredSessions = sessions.filter((s) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'active') return s.status === 'active' || s.status === 'completed';
    if (activeTab === 'archived') return s.status === 'archived';
    return true;
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const SessionCard = ({ session }: { session: Session }) => (
    <Card
      className="cursor-pointer hover:border-primary/50 transition-colors"
      onClick={() => navigate(`/projects/${projectId}/sessions/${session.id}`)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">{session.name}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className={`${statusColors[session.status]} text-white border-0`}
            >
              {statusLabels[session.status]}
            </Badge>
            <DropdownMenu>
              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                <Button variant="ghost" size="icon">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {session.status !== 'archived' && (
                  <DropdownMenuItem
                    onClick={(e) => {
                      e.stopPropagation();
                      handleArchiveSession(session.id);
                    }}
                  >
                    <Archive className="h-4 w-4 mr-2" />
                    Archive
                  </DropdownMenuItem>
                )}
                <DropdownMenuItem
                  className="text-destructive"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteSession(session.id);
                  }}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        {session.description && (
          <CardDescription>{session.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <Brain className="h-4 w-4" />
              <span>{session.memory_count || 0} memories</span>
            </div>
            <div className="flex items-center gap-1">
              <FileText className="h-4 w-4" />
              <span>{session.cell_count || 0} cells</span>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>{formatDate(session.created_at)}</span>
          </div>
        </div>
        {session.initial_prompt && (
          <div className="mt-3 p-2 bg-muted rounded-md text-sm truncate">
            <span className="text-muted-foreground">Prompt: </span>
            {session.initial_prompt}
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Sessions</h1>
          <p className="text-muted-foreground">
            Research sessions with multi-agent interactions
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Session
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Create Research Session</DialogTitle>
              <DialogDescription>
                Start a new session to research a hypothesis with AI agents.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Session Name</Label>
                <Input
                  id="name"
                  placeholder="My Research Session"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Input
                  id="description"
                  placeholder="Brief description of this session"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="initial_prompt">Research Prompt</Label>
                <Textarea
                  id="initial_prompt"
                  placeholder="Describe what you want the agents to research..."
                  rows={4}
                  value={formData.initial_prompt}
                  onChange={(e) =>
                    setFormData({ ...formData, initial_prompt: e.target.value })
                  }
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleCreateSession()} disabled={!formData.name}>
                <Play className="h-4 w-4 mr-2" />
                Start Session
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)}>
        <TabsList>
          <TabsTrigger value="all">All Sessions</TabsTrigger>
          <TabsTrigger value="active">Active</TabsTrigger>
          <TabsTrigger value="archived">Archived</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-6">
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">
              Loading sessions...
            </div>
          ) : filteredSessions.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium">No sessions yet</h3>
              <p className="text-muted-foreground mb-4">
                Create a new session to start researching with AI agents.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Session
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredSessions.map((session) => (
                <SessionCard key={session.id} session={session} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
