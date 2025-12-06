import { useState } from 'react';
import { useTeamStore } from '@/stores/teamStore';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import type { TeamRole } from '@/types/team';

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
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Invite Member</DialogTitle>
          <DialogDescription>
            Add a new member to your team by entering their user ID or email address
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            {error && (
              <div className="bg-destructive/10 border border-destructive text-destructive px-3 py-2 rounded text-sm">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="user_id">User ID or Email *</Label>
              <Input
                id="user_id"
                value={formData.user_id}
                onChange={(e) =>
                  setFormData({ ...formData, user_id: e.target.value })
                }
                placeholder="user@example.com"
                disabled={isLoading}
                autoFocus
                required
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
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                  setFormData({ ...formData, role: e.target.value as TeamRole })
                }
                disabled={isLoading}
              >
                <option value="admin">Admin - Can manage members and settings</option>
                <option value="member">Member - Can collaborate on projects</option>
                <option value="viewer">Viewer - Can view projects only</option>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Inviting...' : 'Invite'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
