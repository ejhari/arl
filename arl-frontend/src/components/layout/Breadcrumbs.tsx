import { Link, useLocation, useParams } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import { Fragment, useEffect, useState } from 'react';
import { useCanvasStore } from '@/stores/canvasStore';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbContext {
  projectName?: string;
  documentTitle?: string;
}

function getBreadcrumbs(pathname: string, context: BreadcrumbContext): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [{ label: 'Home', href: '/dashboard' }];

  let currentPath = '';
  for (let i = 0; i < segments.length; i++) {
    const segment = segments[i];

    // Skip 'view' segment as it's just a routing artifact
    if (segment === 'view') {
      continue;
    }

    currentPath += `/${segment}`;

    // Format segment
    let label = segment.charAt(0).toUpperCase() + segment.slice(1);
    label = label.replace(/-/g, ' ');

    // Check if it's a UUID (don't show full UUID)
    if (segment.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
      const prevSegment = segments[i - 1];

      // Project name for canvas or documents routes
      if (context.projectName && (prevSegment === 'canvas' || prevSegment === 'documents')) {
        label = context.projectName;
      }
      // Document title for view routes
      else if (context.documentTitle && prevSegment === 'view') {
        label = context.documentTitle;
      }
      else {
        label = 'Details';
      }
    }

    // Special handling for route segments
    if (segment === 'canvas') {
      label = 'Projects';
      // Update the href to point to /projects instead of /canvas
      breadcrumbs.push({
        label,
        href: i === segments.length - 1 ? undefined : '/projects',
      });
      continue;
    } else if (segment === 'documents') {
      label = 'Documents';
    }

    breadcrumbs.push({
      label,
      href: i === segments.length - 1 ? undefined : currentPath,
    });
  }

  return breadcrumbs;
}

export function Breadcrumbs() {
  const location = useLocation();
  const params = useParams();
  const { currentProject, projects, loadProject } = useCanvasStore();
  const [projectName, setProjectName] = useState<string | undefined>();
  const [documentTitle, setDocumentTitle] = useState<string | undefined>();

  // Try to get project name from various sources
  useEffect(() => {
    const projectId = params.projectId;
    if (projectId) {
      // First check current project
      if (currentProject?.id === projectId) {
        setProjectName(currentProject.name);
      } else {
        // Fall back to projects list
        const project = projects.find((p) => p.id === projectId);
        if (project) {
          setProjectName(project.name);
        } else {
          // Load project if not in store
          loadProject(projectId).catch(() => {
            // Ignore errors, fallback to "Details"
          });
        }
      }
    } else {
      setProjectName(undefined);
    }
  }, [params.projectId, currentProject, projects, loadProject]);

  // Try to get document title from page context
  useEffect(() => {
    const documentId = params.documentId;
    if (documentId) {
      // Document title will be set by the DocumentViewerPage via a custom event
      const handleDocumentLoad = (event: CustomEvent<{ title: string }>) => {
        setDocumentTitle(event.detail.title);
      };

      window.addEventListener('document-loaded' as never, handleDocumentLoad as EventListener);
      return () => {
        window.removeEventListener('document-loaded' as never, handleDocumentLoad as EventListener);
      };
    } else {
      setDocumentTitle(undefined);
    }
  }, [params.documentId]);

  const breadcrumbs = getBreadcrumbs(location.pathname, { projectName, documentTitle });

  if (breadcrumbs.length <= 1) {
    return null;
  }

  return (
    <nav className="flex items-center space-x-1 text-sm text-muted-foreground" aria-label="Breadcrumb">
      {breadcrumbs.map((crumb, index) => (
        <Fragment key={crumb.href || `${crumb.label}-${index}`}>
          {index > 0 && <ChevronRight className="h-4 w-4" aria-hidden="true" />}
          {crumb.href ? (
            <Link
              to={crumb.href}
              className="hover:text-foreground transition-colors"
            >
              {index === 0 ? (
                <Home className="h-4 w-4" aria-label="Home" />
              ) : (
                crumb.label
              )}
            </Link>
          ) : (
            <span className="text-foreground font-medium" aria-current="page">
              {crumb.label}
            </span>
          )}
        </Fragment>
      ))}
    </nav>
  );
}
