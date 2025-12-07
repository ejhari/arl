import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { canvasAPI } from '@/api/canvas';
import { documentsAPI } from '@/api/documents';
import { useAgentStore } from '@/stores/agentStore';
import { useSessionStore } from '@/stores/sessionStore';
import type { Project } from '@/types/canvas';
import type { Agent, ProjectAgent } from '@/types/agent';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import {
  FolderKanban,
  Bot,
  MessageSquare,
  FileText,
  ArrowLeft,
  Play,
  ExternalLink,
} from 'lucide-react';

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const {
    agents,
    projectAgents,
    isLoading: agentsLoading,
    fetchAgents,
    fetchProjectAgents,
    enableAgentForProject,
    disableAgentForProject,
  } = useAgentStore();

  const { sessions, fetchSessions } = useSessionStore();

  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [togglingAgent, setTogglingAgent] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('sessions');
  const [documentCount, setDocumentCount] = useState<number>(0);

  useEffect(() => {
    if (projectId) {
      loadProject();
      fetchAgents();
      fetchProjectAgents(projectId);
      fetchSessions(projectId);
      loadDocumentCount();
    }
  }, [projectId, fetchAgents, fetchProjectAgents, fetchSessions]);

  const loadDocumentCount = async () => {
    if (!projectId) return;
    try {
      const docs = await documentsAPI.listDocuments(projectId);
      setDocumentCount(docs.length);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const loadProject = async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await canvasAPI.getProject(projectId);
      setProject(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load project');
    } finally {
      setIsLoading(false);
    }
  };

  const isAgentEnabled = (agentId: string): boolean => {
    return projectAgents.some((pa) => pa.agent_id === agentId && pa.is_enabled);
  };

  const getProjectAgent = (agentId: string): ProjectAgent | undefined => {
    return projectAgents.find((pa) => pa.agent_id === agentId);
  };

  const handleToggleAgent = async (agent: Agent) => {
    if (!projectId) return;
    setTogglingAgent(agent.id);

    try {
      const existingPA = getProjectAgent(agent.id);

      if (existingPA) {
        // Disable agent
        await disableAgentForProject(projectId, agent.id);
      } else {
        // Enable agent
        await enableAgentForProject(projectId, {
          agent_id: agent.id,
          is_enabled: true,
        });
      }
    } catch (err) {
      console.error('Failed to toggle agent:', err);
    } finally {
      setTogglingAgent(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <p className="text-destructive mb-4">{error || 'Project not found'}</p>
        <Button variant="outline" onClick={() => navigate('/projects')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Projects
        </Button>
      </div>
    );
  }

  const activeAgents = agents.filter((a) => a.is_active);
  const activeSessions = sessions.filter((s) => s.status === 'active');

  // System agents are always enabled, plus explicitly enabled project agents
  const systemAgents = agents.filter((a) => a.is_system && a.is_active);
  const enabledCustomAgents = projectAgents.filter((pa) => pa.is_enabled);
  const enabledAgentCount = systemAgents.length + enabledCustomAgents.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/projects')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <div className="bg-primary/10 rounded-lg p-2">
                <FolderKanban className="h-6 w-6 text-primary" />
              </div>
              <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
            </div>
            {project.description && (
              <p className="text-muted-foreground mt-2 ml-12">
                {project.description}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link to={`/projects/${projectId}/sessions`}>
            <Button variant="outline">
              <MessageSquare className="h-4 w-4 mr-2" />
              Sessions
            </Button>
          </Link>
          <Link to={`/canvas/${projectId}`}>
            <Button>
              <Play className="h-4 w-4 mr-2" />
              Open Canvas
            </Button>
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeSessions.length}</div>
            <button
              onClick={() => setActiveTab('sessions')}
              className="text-xs text-muted-foreground hover:text-primary hover:underline cursor-pointer"
            >
              {sessions.length} total sessions
            </button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Enabled Agents</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{enabledAgentCount}</div>
            <button
              onClick={() => setActiveTab('agents')}
              className="text-xs text-muted-foreground hover:text-primary hover:underline cursor-pointer"
            >
              {activeAgents.length} available agents
            </button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{documentCount}</div>
            <Link
              to={`/documents/${projectId}`}
              className="text-xs text-muted-foreground hover:text-primary hover:underline"
            >
              View documents
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Canvas</CardTitle>
            <FolderKanban className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <Link
              to={`/canvas/${projectId}`}
              className="text-sm text-primary hover:underline"
            >
              Open workspace
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList>
          <TabsTrigger value="sessions">
            <MessageSquare className="h-4 w-4 mr-2" />
            Recent Sessions ({activeSessions.length})
          </TabsTrigger>
          <TabsTrigger value="agents">
            <Bot className="h-4 w-4 mr-2" />
            Agents ({activeAgents.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sessions" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Sessions</CardTitle>
                  <CardDescription>
                    Active research sessions in this project
                  </CardDescription>
                </div>
                <Link to={`/projects/${projectId}/sessions`}>
                  <Button>
                    <MessageSquare className="h-4 w-4 mr-2" />
                    View All Sessions
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              {activeSessions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No active sessions.{' '}
                  <Link
                    to={`/projects/${projectId}/sessions`}
                    className="text-primary hover:underline"
                  >
                    Start a new session
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {activeSessions.slice(0, 5).map((session) => (
                    <Link
                      key={session.id}
                      to={`/projects/${projectId}/sessions/${session.id}`}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <MessageSquare className="h-4 w-4 text-primary" />
                        <div>
                          <span className="font-medium">{session.name}</span>
                          {session.description && (
                            <p className="text-sm text-muted-foreground truncate max-w-md">
                              {session.description}
                            </p>
                          )}
                        </div>
                      </div>
                      <Badge variant="outline" className="bg-green-500 text-white border-0">
                        Active
                      </Badge>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agents" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Project Agents</CardTitle>
              <CardDescription>
                Enable or disable AI agents for this project. Enabled agents can be used in research sessions.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {agentsLoading ? (
                <div className="flex justify-center py-8">
                  <LoadingSpinner />
                </div>
              ) : activeAgents.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No agents available. Create agents in{' '}
                  <Link to="/settings/agents" className="text-primary hover:underline">
                    Agent Settings
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {activeAgents.map((agent) => (
                    <div
                      key={agent.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        <div className="bg-primary/10 rounded-lg p-2">
                          <Bot className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{agent.display_name}</span>
                            <Badge variant={agent.is_system ? 'secondary' : 'outline'}>
                              {agent.is_system ? 'System' : 'Custom'}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {agent.description}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <code className="text-xs bg-muted px-1 rounded">
                              {agent.name}
                            </code>
                            {agent.version && (
                              <span className="text-xs text-muted-foreground">
                                v{agent.version}
                              </span>
                            )}
                            {agent.service_endpoint && (
                              <a
                                href={agent.service_endpoint}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-primary hover:underline flex items-center gap-1"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <ExternalLink className="h-3 w-3" />
                                Endpoint
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        {agent.is_system ? (
                          <Badge variant="outline" className="bg-green-500/20 text-green-700 border-green-500/50">
                            Enabled
                          </Badge>
                        ) : (
                          <Switch
                            checked={isAgentEnabled(agent.id)}
                            onCheckedChange={() => handleToggleAgent(agent)}
                            disabled={togglingAgent === agent.id}
                          />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

      </Tabs>
    </div>
  );
}
