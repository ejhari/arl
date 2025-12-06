import { useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { useCanvasStore } from '@/stores/canvasStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, TrendingUp, Folder } from 'lucide-react';

export function DashboardPage() {
  const { user } = useAuthStore();
  const { projects, loadProjects } = useCanvasStore();

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  // Calculate summary stats
  const totalProjects = projects.length;
  const recentProjects = projects.slice(0, 3);
  const todayDate = new Date().toLocaleDateString();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground mt-1">
          Welcome back, {user?.full_name || user?.username}!
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <Folder className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalProjects}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Active research projects
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{recentProjects.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Projects updated recently
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayDate}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Current date
            </p>
          </CardContent>
        </Card>
      </div>

    </div>
  );
}
