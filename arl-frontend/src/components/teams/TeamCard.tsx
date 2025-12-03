import { Link } from 'react-router-dom';
import type { Team } from '@/types/team';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, Crown } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

interface TeamCardProps {
  team: Team;
}

export function TeamCard({ team }: TeamCardProps) {
  const { user } = useAuthStore();
  const isOwner = user?.id === team.owner_id;

  return (
    <Link to={`/teams/${team.id}`}>
      <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-4">
          <div className="bg-primary/10 rounded-lg p-3">
            <Users className="h-6 w-6 text-primary" />
          </div>
          {isOwner && (
            <Badge variant="secondary" className="gap-1">
              <Crown className="h-3 w-3" />
              Owner
            </Badge>
          )}
        </div>

        <h3 className="font-semibold text-lg mb-2 line-clamp-1">{team.name}</h3>

        {team.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
            {team.description}
          </p>
        )}

        <div className="flex items-center text-sm text-muted-foreground">
          <Users className="h-4 w-4 mr-1" />
          <span>
            {team.member_count || 0} {team.member_count === 1 ? 'member' : 'members'}
          </span>
        </div>
      </Card>
    </Link>
  );
}
