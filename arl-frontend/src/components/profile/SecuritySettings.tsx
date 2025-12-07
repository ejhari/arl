import { useState, useMemo } from 'react';
import { useProfileStore } from '@/stores/profileStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function SecuritySettings() {
  const { changePassword, isUpdating, error, clearError } = useProfileStore();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [success, setSuccess] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Real-time validation
  const validation = useMemo(() => {
    const errors: string[] = [];

    if (newPassword && newPassword.length < 8) {
      errors.push('Password must be at least 8 characters');
    }

    if (confirmPassword && newPassword !== confirmPassword) {
      errors.push('Passwords do not match');
    }

    return {
      isValid: errors.length === 0 && currentPassword.length > 0 && newPassword.length >= 8 && confirmPassword.length >= 8,
      errors,
      passwordsMatch: !confirmPassword || newPassword === confirmPassword,
      passwordLengthOk: !newPassword || newPassword.length >= 8,
    };
  }, [currentPassword, newPassword, confirmPassword]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError(null);
    setSuccess(false);

    // Final validation before submit
    if (!currentPassword) {
      setValidationError('Current password is required');
      return;
    }

    if (newPassword.length < 8) {
      setValidationError('New password must be at least 8 characters long');
      return;
    }

    if (newPassword !== confirmPassword) {
      setValidationError('New passwords do not match');
      return;
    }

    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      // Clear form and show success
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setSuccess(true);

      // Hide success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      // Error handled by store
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change Password</CardTitle>
        <CardDescription>Update your password to keep your account secure</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {(error || validationError) && (
            <div className="rounded-md bg-red-50 dark:bg-red-950 p-3 text-sm text-red-600 dark:text-red-400">
              {error || validationError}
            </div>
          )}

          {success && (
            <div className="rounded-md bg-green-50 dark:bg-green-950 p-3 text-sm text-green-600 dark:text-green-400">
              Password changed successfully!
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="currentPassword">Current Password</Label>
            <Input
              id="currentPassword"
              type="password"
              value={currentPassword}
              onChange={(e) => {
                setCurrentPassword(e.target.value);
                setValidationError(null);
              }}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="newPassword">New Password</Label>
            <Input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(e) => {
                setNewPassword(e.target.value);
                setValidationError(null);
              }}
              minLength={8}
              required
              className={newPassword && !validation.passwordLengthOk ? 'border-red-500' : ''}
            />
            <p className={`text-xs ${newPassword && !validation.passwordLengthOk ? 'text-red-500' : 'text-muted-foreground'}`}>
              Password must be at least 8 characters long
              {newPassword && validation.passwordLengthOk && (
                <span className="text-green-500 ml-2">✓</span>
              )}
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm New Password</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                setValidationError(null);
              }}
              minLength={8}
              required
              className={confirmPassword && !validation.passwordsMatch ? 'border-red-500' : ''}
            />
            {confirmPassword && !validation.passwordsMatch && (
              <p className="text-xs text-red-500">Passwords do not match</p>
            )}
            {confirmPassword && validation.passwordsMatch && newPassword && (
              <p className="text-xs text-green-500">Passwords match ✓</p>
            )}
          </div>

          <Button type="submit" disabled={isUpdating || !validation.isValid}>
            {isUpdating ? 'Updating...' : 'Change Password'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
