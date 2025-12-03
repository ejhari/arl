import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { TeamWithMembers } from '@/types/team';
import { useTeamStore } from '@/stores/teamStore';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Save, Trash2 } from 'lucide-react';

interface TeamSettingsProps {
  team: TeamWithMembers;
}

export function TeamSettings({ team }: TeamSettingsProps) {
  const navigate = useNavigate();
  const { updateTeam, deleteTeam, isLoading } = useTeamStore();
  const [formData, setFormData] = useState({
    name: team.name,
    description: team.description || '',
  });
  const [hasChanges, setHasChanges] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleChange = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value });
    setHasChanges(true);
    setError(null);
    setSuccess(null);
  };

  const handleSave = async () => {
    if (!formData.name.trim()) {
      setError('Team name is required');
      return;
    }

    try {
      await updateTeam(team.id, {
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
      });
      setHasChanges(false);
      setSuccess('Team settings updated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update team');
    }
  };

  const handleDelete = async () => {
    const confirmed = confirm(
      `Are you sure you want to delete "${team.name}"? This action cannot be undone.`
    );

    if (!confirmed) return;

    try {
      await deleteTeam(team.id);
      navigate('/teams');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete team');
    }
  };

  return (
    <div className="space-y-6">
      {/* General Settings */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">General Settings</h3>

        {error && (
          <div className="bg-destructive/10 border border-destructive text-destructive px-3 py-2 rounded text-sm mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-500/10 border border-green-500 text-green-600 px-3 py-2 rounded text-sm mb-4">
            {success}
          </div>
        )}

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Team Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              disabled={isLoading}
              className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="Describe your team's purpose..."
            />
          </div>

          {hasChanges && (
            <Button onClick={handleSave} disabled={isLoading}>
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </Button>
          )}
        </div>
      </Card>

      {/* Danger Zone */}
      <Card className="p-6 border-destructive">
        <h3 className="text-lg font-semibold text-destructive mb-2">Danger Zone</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Once you delete a team, there is no going back. Please be certain.
        </p>

        <Separator className="my-4" />

        <Button
          variant="destructive"
          onClick={handleDelete}
          disabled={isLoading}
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Delete Team
        </Button>
      </Card>
    </div>
  );
}
