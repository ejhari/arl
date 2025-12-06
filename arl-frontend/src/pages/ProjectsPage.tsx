import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { canvasAPI } from '@/api/canvas';
import type { Project } from '@/types/canvas';
import { CreateProjectDialog } from '@/components/projects/CreateProjectDialog';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Plus, FolderKanban, Calendar } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await canvasAPI.listProjects();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
          <p className="text-muted-foreground mt-1">
            Manage your research projects and notebooks
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
          <div className="bg-muted rounded-full p-6 mb-4">
            <FolderKanban className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold mb-2">No projects yet</h3>
          <p className="text-muted-foreground mb-4 max-w-sm">
            Create your first project to start working on your research
          </p>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Your First Project
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link key={project.id} to={`/canvas/${project.id}`}>
              <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer h-full">
                <div className="flex items-start justify-between mb-4">
                  <div className="bg-primary/10 rounded-lg p-3">
                    <FolderKanban className="h-6 w-6 text-primary" />
                  </div>
                </div>

                <h3 className="font-semibold text-lg mb-2 line-clamp-1">
                  {project.name}
                </h3>

                {project.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                    {project.description}
                  </p>
                )}

                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    <span>
                      {formatDistanceToNow(new Date(project.updated_at), {
                        addSuffix: true,
                      })}
                    </span>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Create Project Dialog */}
      <CreateProjectDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
      />
    </div>
  );
}
