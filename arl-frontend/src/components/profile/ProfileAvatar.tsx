import { useRef, useState } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { useProfileStore } from '@/stores/profileStore';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Camera, Trash2 } from 'lucide-react';

export function ProfileAvatar() {
  const { user } = useAuthStore();
  const { updateAvatar, removeAvatar, isUpdating } = useProfileStore();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const getInitials = (name: string | null | undefined) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image size must be less than 5MB');
      return;
    }

    setUploading(true);
    try {
      await updateAvatar(file);
    } catch (error) {
      console.error('Failed to upload avatar:', error);
      alert(error instanceof Error ? error.message : 'Failed to upload avatar');
    } finally {
      setUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRemove = async () => {
    if (!confirm('Are you sure you want to remove your profile picture?')) {
      return;
    }

    try {
      await removeAvatar();
    } catch (error) {
      console.error('Failed to remove avatar:', error);
      alert(error instanceof Error ? error.message : 'Failed to remove avatar');
    }
  };

  const displayName = user?.full_name || user?.username || 'User';

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <Avatar className="h-32 w-32">
          <AvatarImage src={undefined} alt={displayName} />
          <AvatarFallback className="bg-primary text-primary-foreground text-3xl">
            {getInitials(displayName)}
          </AvatarFallback>
        </Avatar>
        <button
          onClick={handleFileSelect}
          disabled={uploading || isUpdating}
          className="absolute bottom-0 right-0 rounded-full bg-primary p-2 text-primary-foreground shadow-lg hover:bg-primary/90 disabled:opacity-50"
        >
          <Camera className="h-4 w-4" />
        </button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />

      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleFileSelect}
          disabled={uploading || isUpdating}
        >
          {uploading ? 'Uploading...' : 'Change Photo'}
        </Button>
        {user && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleRemove}
            disabled={isUpdating}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
