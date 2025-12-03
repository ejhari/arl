import { useState } from 'react';
import { useTeamStore } from '@/stores/teamStore';
import { Dialog } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import type { TeamRole } from '@/types/team';
import { X, UserPlus } from 'lucide-react';

interface InviteMemberDialogProps {
  teamId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function InviteMemberDialog({
  teamId,
  open,
  onOpenChange,
}: InviteMemberDialogProps) {
  const { addMember, isLoading } = useTeamStore();
  const [formData, setFormData] = useState({
    user_id: '',
    role: 'member' as TeamRole,
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.user_id.trim()) {
      setError('User ID is required');
      return;
    }

    try {
      await addMember(teamId, {
        user_id: formData.user_id.trim(),
        role: formData.role,
      });

      // Reset form and close
      setFormData({ user_id: '', role: 'member' });
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add member');
    }
  };

  const handleClose = () => {
    setFormData({ user_id: '', role: 'member' });
    setError(null);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <div className="bg-card p-6 rounded-lg shadow-lg max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <UserPlus className="h-5 w-5 text-primary" />
            <h2 className="text-2xl font-semibold">Invite Member</h2>
          </div>
          <button
            onClick={handleClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-destructive/10 border border-destructive text-destructive px-3 py-2 rounded text-sm">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="user_id">User ID or Email</Label>
            <Input
              id="user_id"
              value={formData.user_id}
              onChange={(e) =>
                setFormData({ ...formData, user_id: e.target.value })
              }
              placeholder="user@example.com"
              disabled={isLoading}
              autoFocus
            />
            <p className="text-xs text-muted-foreground">
              Enter the user ID or email of the person you want to invite
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Select
              id="role"
              value={formData.role}
              onChange={(e) =>
                setFormData({ ...formData, role: e.target.value as TeamRole })
              }
              disabled={isLoading}
            >
              <option value="admin">Admin - Can manage members and settings</option>
              <option value="member">Member - Can collaborate on projects</option>
              <option value="viewer">Viewer - Can view projects only</option>
            </Select>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="flex-1">
              {isLoading ? 'Inviting...' : 'Invite'}
            </Button>
          </div>
        </form>
      </div>
    </Dialog>
  );
}
