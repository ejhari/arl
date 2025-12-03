import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTeamStore } from '@/stores/teamStore';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs } from '@/components/ui/tabs';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { TeamMembersList } from '@/components/teams/TeamMembersList';
import { InviteMemberDialog } from '@/components/teams/InviteMemberDialog';
import { TeamSettings } from '@/components/teams/TeamSettings';
import { UserPlus, Settings, Users, ArrowLeft } from 'lucide-react';

export function TeamDetailPage() {
  const { teamId } = useParams<{ teamId: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { currentTeam, isLoading, error, fetchTeam } = useTeamStore();
  const [activeTab, setActiveTab] = useState('members');
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);

  useEffect(() => {
    if (teamId) {
      fetchTeam(teamId);
    }
  }, [teamId, fetchTeam]);

  if (isLoading && !currentTeam) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !currentTeam) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" onClick={() => navigate('/teams')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Teams
        </Button>
        <Card className="p-6">
          <p className="text-destructive">{error || 'Team not found'}</p>
        </Card>
      </div>
    );
  }

  const isOwner = user?.id === currentTeam.owner_id;
  const isAdmin = currentTeam.members.find((m) => m.user_id === user?.id)?.role === 'admin';
  const canManageMembers = isOwner || isAdmin;

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button variant="ghost" onClick={() => navigate('/teams')}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Teams
      </Button>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{currentTeam.name}</h1>
          {currentTeam.description && (
            <p className="text-muted-foreground mt-1">{currentTeam.description}</p>
          )}
        </div>
        {canManageMembers && (
          <Button onClick={() => setInviteDialogOpen(true)}>
            <UserPlus className="h-4 w-4 mr-2" />
            Invite Member
          </Button>
        )}
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="bg-primary/10 rounded-lg p-3">
              <Users className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{currentTeam.members.length}</p>
              <p className="text-sm text-muted-foreground">
                {currentTeam.members.length === 1 ? 'Member' : 'Members'}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="border-b border-border">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('members')}
              className={`pb-3 px-1 text-sm font-medium transition-colors border-b-2 ${
                activeTab === 'members'
                  ? 'border-primary text-foreground'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <Users className="h-4 w-4 inline mr-2" />
              Members
            </button>
            {isOwner && (
              <button
                onClick={() => setActiveTab('settings')}
                className={`pb-3 px-1 text-sm font-medium transition-colors border-b-2 ${
                  activeTab === 'settings'
                    ? 'border-primary text-foreground'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                <Settings className="h-4 w-4 inline mr-2" />
                Settings
              </button>
            )}
          </div>
        </div>

        <div className="mt-6">
          {activeTab === 'members' && (
            <TeamMembersList
              team={currentTeam}
              canManage={canManageMembers}
            />
          )}
          {activeTab === 'settings' && isOwner && (
            <TeamSettings team={currentTeam} />
          )}
        </div>
      </Tabs>

      {/* Invite Member Dialog */}
      {canManageMembers && (
        <InviteMemberDialog
          teamId={currentTeam.id}
          open={inviteDialogOpen}
          onOpenChange={setInviteDialogOpen}
        />
      )}
    </div>
  );
}
