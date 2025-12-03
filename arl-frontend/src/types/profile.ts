export interface ProfileUpdate {
  full_name?: string;
  email?: string;
  username?: string;
  bio?: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface ProfileState {
  isUpdating: boolean;
  error: string | null;
  updateProfile: (data: ProfileUpdate) => Promise<void>;
  updateAvatar: (file: File) => Promise<void>;
  removeAvatar: () => Promise<void>;
  changePassword: (data: PasswordChange) => Promise<void>;
  clearError: () => void;
}
