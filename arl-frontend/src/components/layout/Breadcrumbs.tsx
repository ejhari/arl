import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import { Fragment } from 'react';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

function getBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [{ label: 'Home', href: '/dashboard' }];

  let currentPath = '';
  for (let i = 0; i < segments.length; i++) {
    currentPath += `/${segments[i]}`;
    const segment = segments[i];

    // Format segment
    let label = segment.charAt(0).toUpperCase() + segment.slice(1);
    label = label.replace(/-/g, ' ');

    // Check if it's a UUID (don't show full UUID)
    if (segment.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
      label = 'Details';
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
  const breadcrumbs = getBreadcrumbs(location.pathname);

  if (breadcrumbs.length <= 1) {
    return null;
  }

  return (
    <nav className="flex items-center space-x-1 text-sm text-muted-foreground">
      {breadcrumbs.map((crumb, index) => (
        <Fragment key={crumb.href || crumb.label}>
          {index > 0 && <ChevronRight className="h-4 w-4" />}
          {crumb.href ? (
            <Link
              to={crumb.href}
              className="hover:text-foreground transition-colors"
            >
              {index === 0 ? (
                <Home className="h-4 w-4" />
              ) : (
                crumb.label
              )}
            </Link>
          ) : (
            <span className="text-foreground font-medium">{crumb.label}</span>
          )}
        </Fragment>
      ))}
    </nav>
  );
}
