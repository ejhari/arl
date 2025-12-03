import { Outlet } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { CommandPalette } from '@/components/layout/CommandPalette';
import { UserMenu } from '@/components/UserMenu';

export function MainLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />

      <div className="pl-64 transition-all duration-300">
        {/* Top Header */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-card px-6">
          <div className="flex flex-1 items-center gap-4">
            <Breadcrumbs />
          </div>
          <div className="flex items-center gap-4">
            <CommandPalette />
            <UserMenu />
          </div>
        </header>

        {/* Main Content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
