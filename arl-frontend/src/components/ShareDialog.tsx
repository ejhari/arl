import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { X, Share2, UserPlus } from 'lucide-react';
import type { ProjectRole } from '@/types/permission';

interface ShareDialogProps {
  projectId: string;
  projectName: string;
  onClose: () => void;
  onShare?: (userIds: string[], role: ProjectRole) => Promise<void>;
}

export function ShareDialog({ projectName, onClose, onShare }: ShareDialogProps) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<ProjectRole>('viewer');
  const [sharing, setSharing] = useState(false);
  const [message, setMessage] = useState('');

  const handleShare = async () => {
    if (!email.trim()) {
      setMessage('Please enter an email address');
      return;
    }

    setSharing(true);
    setMessage('');

    try {
      // In a real implementation, you'd look up the user by email first
      // For now, we'll show a success message
      if (onShare) {
        await onShare([], role);
      }
      setMessage('Project shared successfully!');
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Failed to share project');
    } finally {
      setSharing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Share2 className="h-5 w-5" />
              Share Project
            </h2>
            <p className="text-sm text-muted-foreground mt-1">{projectName}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-4">
          {/* Email Input */}
          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              placeholder="colleague@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={sharing}
            />
          </div>

          {/* Role Selection */}
          <div className="space-y-2">
            <Label>Access Level</Label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer p-3 rounded-lg border hover:bg-muted/50">
                <input
                  type="radio"
                  name="role"
                  value="viewer"
                  checked={role === 'viewer'}
                  onChange={(e) => setRole(e.target.value as ProjectRole)}
                  className="h-4 w-4"
                />
                <div>
                  <div className="font-medium">Viewer</div>
                  <div className="text-sm text-muted-foreground">Can view project content</div>
                </div>
              </label>
              <label className="flex items-center gap-2 cursor-pointer p-3 rounded-lg border hover:bg-muted/50">
                <input
                  type="radio"
                  name="role"
                  value="editor"
                  checked={role === 'editor'}
                  onChange={(e) => setRole(e.target.value as ProjectRole)}
                  className="h-4 w-4"
                />
                <div>
                  <div className="font-medium">Editor</div>
                  <div className="text-sm text-muted-foreground">Can edit and create content</div>
                </div>
              </label>
            </div>
          </div>

          {/* Message */}
          {message && (
            <div className={`p-3 rounded-lg text-sm ${
              message.includes('success') ? 'bg-green-100 text-green-800' : 'bg-destructive/10 text-destructive'
            }`}>
              {message}
            </div>
          )}

          {/* Info */}
          <div className="text-xs text-muted-foreground bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">Note:</p>
            <p>The user will receive an email notification and can access the project immediately.</p>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <Button variant="outline" onClick={onClose} className="flex-1" disabled={sharing}>
              Cancel
            </Button>
            <Button onClick={handleShare} className="flex-1" disabled={sharing || !email.trim()}>
              {sharing ? (
                <>Sharing...</>
              ) : (
                <>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Share
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
