import { Link } from 'react-router-dom';
import type { Team } from '@/types/team';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
      <Card className="hover:border-primary hover:shadow-md transition-all cursor-pointer group h-full">
        <CardHeader>
          <div className="flex items-start justify-between mb-3">
            <div className="bg-primary/10 rounded-lg p-3 group-hover:bg-primary/20 transition-colors">
              <Users className="h-6 w-6 text-primary" />
            </div>
            {isOwner && (
              <Badge variant="secondary" className="gap-1">
                <Crown className="h-3 w-3" />
                Owner
              </Badge>
            )}
          </div>

          <CardTitle className="group-hover:text-primary transition-colors">
            {team.name}
          </CardTitle>
        </CardHeader>

        <CardContent>
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
        </CardContent>
      </Card>
    </Link>
  );
}
