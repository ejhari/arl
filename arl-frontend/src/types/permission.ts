export type ProjectRole = 'owner' | 'editor' | 'viewer';

export interface ProjectPermission {
  id: string;
  project_id: string;
  user_id: string;
  username: string;
  email: string;
  role: ProjectRole;
  granted_by: string;
  granted_at: string;
}

export interface CreatePermissionData {
  user_id: string;
  role?: ProjectRole;
}

export interface ShareProjectData {
  user_ids: string[];
  role?: ProjectRole;
}
