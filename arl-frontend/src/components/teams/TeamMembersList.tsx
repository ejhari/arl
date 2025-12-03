import { useState } from 'react';
import type { TeamWithMembers, TeamMember, TeamRole } from '@/types/team';
import { useTeamStore } from '@/stores/teamStore';
import { useAuthStore } from '@/stores/authStore';
import { Card } from '@/components/ui/card';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Crown, Shield, User, Eye, MoreVertical, Trash2 } from 'lucide-react';

interface TeamMembersListProps {
  team: TeamWithMembers;
  canManage: boolean;
}

const roleIcons = {
  owner: Crown,
  admin: Shield,
  member: User,
  viewer: Eye,
};

const roleColors = {
  owner: 'default' as const,
  admin: 'secondary' as const,
  member: 'outline' as const,
  viewer: 'outline' as const,
};

export function TeamMembersList({ team, canManage }: TeamMembersListProps) {
  const { user } = useAuthStore();
  const { updateMemberRole, removeMember, isLoading } = useTeamStore();
  const [updatingMember, setUpdatingMember] = useState<string | null>(null);

  const handleRoleChange = async (member: TeamMember, newRole: TeamRole) => {
    if (member.role === 'owner' || newRole === member.role) return;

    setUpdatingMember(member.user_id);
    try {
      await updateMemberRole(team.id, member.user_id, newRole);
    } catch (error) {
      console.error('Failed to update member role:', error);
    } finally {
      setUpdatingMember(null);
    }
  };

  const handleRemoveMember = async (member: TeamMember) => {
    if (member.role === 'owner') return;

    if (!confirm(`Remove ${member.username} from the team?`)) return;

    try {
      await removeMember(team.id, member.user_id);
    } catch (error) {
      console.error('Failed to remove member:', error);
    }
  };

  const sortedMembers = [...team.members].sort((a, b) => {
    const roleOrder = { owner: 0, admin: 1, member: 2, viewer: 3 };
    return roleOrder[a.role] - roleOrder[b.role];
  });

  return (
    <div className="space-y-3">
      {sortedMembers.map((member) => {
        const Icon = roleIcons[member.role];
        const isCurrentUser = member.user_id === user?.id;
        const isOwner = member.role === 'owner';
        const canModify = canManage && !isOwner && !isCurrentUser;

        return (
          <Card key={member.user_id} className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Avatar>
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-primary font-medium">
                      {member.username[0].toUpperCase()}
                    </span>
                  </div>
                </Avatar>

                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">
                      {member.username}
                      {isCurrentUser && (
                        <span className="text-muted-foreground ml-2">(You)</span>
                      )}
                    </p>
                  </div>
                  <p className="text-sm text-muted-foreground">{member.email}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {canModify && !updatingMember ? (
                  <Select
                    value={member.role}
                    onChange={(e) =>
                      handleRoleChange(member, e.target.value as TeamRole)
                    }
                    disabled={isLoading}
                  >
                    <option value="admin">Admin</option>
                    <option value="member">Member</option>
                    <option value="viewer">Viewer</option>
                  </Select>
                ) : (
                  <Badge variant={roleColors[member.role]}>
                    <Icon className="h-3 w-3 mr-1" />
                    {member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                  </Badge>
                )}

                {canModify && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() => handleRemoveMember(member)}
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Remove from team
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
