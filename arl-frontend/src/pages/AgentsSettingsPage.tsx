import { useEffect, useState } from 'react';
import { useAgentStore } from '@/stores/agentStore';
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
  Bot,
  Plus,
  Settings,
  Trash2,
  Power,
  PowerOff,
  ExternalLink,
} from 'lucide-react';
import type { Agent, CreateAgentData } from '@/types/agent';

export default function AgentsSettingsPage() {
  const {
    agents,
    isLoading,
    error,
    fetchAgents,
    createAgent,
    updateAgent,
    deleteAgent,
  } = useAgentStore();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [_selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [formData, setFormData] = useState<CreateAgentData>({
    name: '',
    display_name: '',
    description: '',
    service_endpoint: '',
    version: '1.0.0',
    protocol_version: '0.3',
  });

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const systemAgents = agents.filter((a) => a.is_system);
  const customAgents = agents.filter((a) => !a.is_system);

  const handleCreateAgent = async () => {
    try {
      await createAgent(formData);
      setIsCreateDialogOpen(false);
      resetForm();
    } catch (err) {
      console.error('Failed to create agent:', err);
    }
  };

  const handleToggleAgent = async (agent: Agent) => {
    try {
      await updateAgent(agent.id, { is_active: !agent.is_active });
    } catch (err) {
      console.error('Failed to toggle agent:', err);
    }
  };

  const handleDeleteAgent = async (agentId: string) => {
    if (confirm('Are you sure you want to delete this agent?')) {
      try {
        await deleteAgent(agentId);
      } catch (err) {
        console.error('Failed to delete agent:', err);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      display_name: '',
      description: '',
      service_endpoint: '',
      version: '1.0.0',
      protocol_version: '0.3',
    });
  };

  const AgentCard = ({ agent }: { agent: Agent }) => (
    <Card className={!agent.is_active ? 'opacity-60' : ''}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">{agent.display_name}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={agent.is_system ? 'secondary' : 'outline'}>
              {agent.is_system ? 'System' : 'Custom'}
            </Badge>
            <Badge variant={agent.is_active ? 'default' : 'destructive'}>
              {agent.is_active ? 'Active' : 'Inactive'}
            </Badge>
          </div>
        </div>
        <CardDescription>{agent.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            <span className="font-mono">{agent.name}</span>
            {agent.version && <span className="ml-2">v{agent.version}</span>}
          </div>
          <div className="flex items-center gap-2">
            {agent.service_endpoint && (
              <a
                href={agent.service_endpoint}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center h-10 w-10 rounded-md hover:bg-accent hover:text-accent-foreground"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            )}
            {!agent.is_system && (
              <>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleToggleAgent(agent)}
                >
                  {agent.is_active ? (
                    <PowerOff className="h-4 w-4" />
                  ) : (
                    <Power className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setSelectedAgent(agent)}
                >
                  <Settings className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDeleteAgent(agent.id)}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Agents</h1>
          <p className="text-muted-foreground">
            Manage AI agents available for your projects
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Agent
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Create Custom Agent</DialogTitle>
              <DialogDescription>
                Add a new AI agent to your agent pool. Custom agents can be
                enabled per project.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Agent ID</Label>
                <Input
                  id="name"
                  placeholder="my-custom-agent"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="display_name">Display Name</Label>
                <Input
                  id="display_name"
                  placeholder="My Custom Agent"
                  value={formData.display_name}
                  onChange={(e) =>
                    setFormData({ ...formData, display_name: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="What does this agent do?"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="service_endpoint">Service Endpoint (Optional)</Label>
                <Input
                  id="service_endpoint"
                  placeholder="https://api.example.com/agent"
                  value={formData.service_endpoint}
                  onChange={(e) =>
                    setFormData({ ...formData, service_endpoint: e.target.value })
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="version">Version</Label>
                  <Input
                    id="version"
                    placeholder="1.0.0"
                    value={formData.version}
                    onChange={(e) =>
                      setFormData({ ...formData, version: e.target.value })
                    }
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="protocol_version">A2A Protocol Version</Label>
                  <Input
                    id="protocol_version"
                    placeholder="0.3"
                    value={formData.protocol_version}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        protocol_version: e.target.value,
                      })
                    }
                  />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateAgent} disabled={!formData.name || !formData.display_name}>
                Create Agent
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

      <Tabs defaultValue="all" className="w-full">
        <TabsList>
          <TabsTrigger value="all">All Agents ({agents.length})</TabsTrigger>
          <TabsTrigger value="system">System ({systemAgents.length})</TabsTrigger>
          <TabsTrigger value="custom">Custom ({customAgents.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-6">
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">
              Loading agents...
            </div>
          ) : agents.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No agents found. Create your first custom agent to get started.
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {agents.map((agent) => (
                <AgentCard key={agent.id} agent={agent} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="system" className="mt-6">
          {systemAgents.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No system agents available.
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {systemAgents.map((agent) => (
                <AgentCard key={agent.id} agent={agent} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="custom" className="mt-6">
          {customAgents.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No custom agents yet. Create one to get started.
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {customAgents.map((agent) => (
                <AgentCard key={agent.id} agent={agent} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
