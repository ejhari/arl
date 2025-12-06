import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { canvasAPI } from '@/api/canvas';
import { documentsAPI } from '@/api/documents';
import type { Project } from '@/types/canvas';
import type { Document } from '@/types/document';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { FileText, FolderKanban, ChevronRight, Calendar } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface ProjectWithDocuments extends Project {
  documentCount: number;
  recentDocuments: Document[];
}

export function DocumentsLandingPage() {
  const [projects, setProjects] = useState<ProjectWithDocuments[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjectsWithDocuments();
  }, []);

  const loadProjectsWithDocuments = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const projectsList = await canvasAPI.listProjects();

      // Load documents for each project
      const projectsWithDocs = await Promise.all(
        projectsList.map(async (project) => {
          try {
            const docs = await documentsAPI.listDocuments(project.id);
            return {
              ...project,
              documentCount: docs.length,
              recentDocuments: docs.slice(0, 3), // Get 3 most recent
            };
          } catch (err) {
            console.error(`Failed to load documents for project ${project.id}:`, err);
            return {
              ...project,
              documentCount: 0,
              recentDocuments: [],
            };
          }
        })
      );

      setProjects(projectsWithDocs);
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
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
        <p className="text-muted-foreground mt-1">
          Browse and manage documents across all your projects
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Projects with Documents */}
      {projects.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <div className="bg-muted rounded-full p-6 mb-4">
              <FileText className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No projects yet</h3>
            <p className="text-muted-foreground text-center mb-6 max-w-sm">
              Create a project first to start uploading and managing documents
            </p>
            <Link to="/projects">
              <Button size="lg">
                <FolderKanban className="h-5 w-5 mr-2" />
                Go to Projects
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {projects.map((project) => (
            <Card key={project.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="bg-primary/10 rounded-lg p-2">
                        <FolderKanban className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-xl">{project.name}</CardTitle>
                        {project.description && (
                          <CardDescription className="mt-1">
                            {project.description}
                          </CardDescription>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground mt-3">
                      <div className="flex items-center gap-1">
                        <FileText className="h-4 w-4" />
                        <span>
                          {project.documentCount} {project.documentCount === 1 ? 'document' : 'documents'}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>
                          Updated {formatDistanceToNow(new Date(project.updated_at), { addSuffix: true })}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Link to={`/documents/${project.id}`}>
                    <Button variant="outline">
                      View Documents
                      <ChevronRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </div>
              </CardHeader>

              {project.recentDocuments.length > 0 && (
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground mb-3">Recent Documents</p>
                    <div className="space-y-2">
                      {project.recentDocuments.map((doc) => (
                        <Link
                          key={doc.id}
                          to={`/documents/${project.id}/view/${doc.id}`}
                          className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent transition-colors group"
                        >
                          <span className="text-2xl">{getFileIcon(doc.file_type)}</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium line-clamp-1 group-hover:text-primary transition-colors">
                              {doc.title}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {doc.file_name} • {formatFileSize(doc.file_size)}
                            </p>
                          </div>
                          {doc.is_processed && (
                            <span className="text-xs text-green-600 dark:text-green-400">
                              ✓ Processed
                            </span>
                          )}
                        </Link>
                      ))}
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function getFileIcon(fileType: string): string {
  if (fileType.includes('pdf')) return '📄';
  if (fileType.includes('word') || fileType.includes('doc')) return '📝';
  if (fileType.includes('excel') || fileType.includes('sheet')) return '📊';
  if (fileType.includes('image')) return '🖼️';
  return '📎';
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
