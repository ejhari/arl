export type TeamRole = 'owner' | 'admin' | 'member' | 'viewer';

export interface TeamMember {
  user_id: string;
  username: string;
  email: string;
  role: TeamRole;
  joined_at: string;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
  member_count?: number;
}

export interface TeamWithMembers extends Team {
  members: TeamMember[];
}

export interface CreateTeamData {
  name: string;
  description?: string;
}

export interface UpdateTeamData {
  name?: string;
  description?: string;
}

export interface AddTeamMemberData {
  user_id: string;
  role?: TeamRole;
}
