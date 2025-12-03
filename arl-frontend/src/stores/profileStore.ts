import { create } from 'zustand';
import type { ProfileState, ProfileUpdate, PasswordChange } from '@/types/profile';
import { profileAPI } from '@/api/profile';
import { useAuthStore } from './authStore';

export const useProfileStore = create<ProfileState>((set) => ({
  isUpdating: false,
  error: null,

  updateProfile: async (data: ProfileUpdate) => {
    set({ isUpdating: true, error: null });
    try {
      const accessToken = useAuthStore.getState().accessToken;
      if (!accessToken) {
        throw new Error('Not authenticated');
      }

      const updatedUser = await profileAPI.updateProfile(accessToken, data);

      // Update user in auth store
      useAuthStore.setState({ user: updatedUser });

      set({ isUpdating: false });
    } catch (error) {
      set({
        isUpdating: false,
        error: error instanceof Error ? error.message : 'Failed to update profile',
      });
      throw error;
    }
  },

  updateAvatar: async (file: File) => {
    set({ isUpdating: true, error: null });
    try {
      const accessToken = useAuthStore.getState().accessToken;
      if (!accessToken) {
        throw new Error('Not authenticated');
      }

      const updatedUser = await profileAPI.uploadAvatar(accessToken, file);

      // Update user in auth store
      useAuthStore.setState({ user: updatedUser });

      set({ isUpdating: false });
    } catch (error) {
      set({
        isUpdating: false,
        error: error instanceof Error ? error.message : 'Failed to upload avatar',
      });
      throw error;
    }
  },

  removeAvatar: async () => {
    set({ isUpdating: true, error: null });
    try {
      const accessToken = useAuthStore.getState().accessToken;
      if (!accessToken) {
        throw new Error('Not authenticated');
      }

      const updatedUser = await profileAPI.removeAvatar(accessToken);

      // Update user in auth store
      useAuthStore.setState({ user: updatedUser });

      set({ isUpdating: false });
    } catch (error) {
      set({
        isUpdating: false,
        error: error instanceof Error ? error.message : 'Failed to remove avatar',
      });
      throw error;
    }
  },

  changePassword: async (data: PasswordChange) => {
    set({ isUpdating: true, error: null });
    try {
      const accessToken = useAuthStore.getState().accessToken;
      if (!accessToken) {
        throw new Error('Not authenticated');
      }

      await profileAPI.changePassword(accessToken, data);

      set({ isUpdating: false });
    } catch (error) {
      set({
        isUpdating: false,
        error: error instanceof Error ? error.message : 'Failed to change password',
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
