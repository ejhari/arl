import { create } from 'zustand';
import type { Team, TeamWithMembers, CreateTeamData, UpdateTeamData, AddTeamMemberData, TeamRole } from '@/types/team';
import { teamsAPI } from '@/api/teams';

interface TeamState {
  teams: Team[];
  currentTeam: TeamWithMembers | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchTeams: () => Promise<void>;
  fetchTeam: (teamId: string) => Promise<void>;
  createTeam: (data: CreateTeamData) => Promise<Team>;
  updateTeam: (teamId: string, data: UpdateTeamData) => Promise<void>;
  deleteTeam: (teamId: string) => Promise<void>;
  addMember: (teamId: string, data: AddTeamMemberData) => Promise<void>;
  updateMemberRole: (teamId: string, userId: string, role: TeamRole) => Promise<void>;
  removeMember: (teamId: string, userId: string) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

export const useTeamStore = create<TeamState>((set, get) => ({
  teams: [],
  currentTeam: null,
  isLoading: false,
  error: null,

  fetchTeams: async () => {
    set({ isLoading: true, error: null });
    try {
      const teams = await teamsAPI.listTeams();
      set({ teams, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch teams',
      });
    }
  },

  fetchTeam: async (teamId: string) => {
    set({ isLoading: true, error: null });
    try {
      const team = await teamsAPI.getTeam(teamId);
      set({ currentTeam: team, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch team',
      });
    }
  },

  createTeam: async (data: CreateTeamData) => {
    set({ isLoading: true, error: null });
    try {
      const team = await teamsAPI.createTeam(data);
      set((state) => ({
        teams: [...state.teams, team],
        isLoading: false,
      }));
      return team;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to create team',
      });
      throw error;
    }
  },

  updateTeam: async (teamId: string, data: UpdateTeamData) => {
    set({ isLoading: true, error: null });
    try {
      const updatedTeam = await teamsAPI.updateTeam(teamId, data);
      set((state) => ({
        teams: state.teams.map((t) => (t.id === teamId ? updatedTeam : t)),
        currentTeam: state.currentTeam?.id === teamId
          ? { ...state.currentTeam, ...updatedTeam }
          : state.currentTeam,
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to update team',
      });
      throw error;
    }
  },

  deleteTeam: async (teamId: string) => {
    set({ isLoading: true, error: null });
    try {
      await teamsAPI.deleteTeam(teamId);
      set((state) => ({
        teams: state.teams.filter((t) => t.id !== teamId),
        currentTeam: state.currentTeam?.id === teamId ? null : state.currentTeam,
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to delete team',
      });
      throw error;
    }
  },

  addMember: async (teamId: string, data: AddTeamMemberData) => {
    set({ isLoading: true, error: null });
    try {
      const updatedTeam = await teamsAPI.addMember(teamId, data);
      set({ currentTeam: updatedTeam, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to add member',
      });
      throw error;
    }
  },

  updateMemberRole: async (teamId: string, userId: string, role: TeamRole) => {
    set({ isLoading: true, error: null });
    try {
      const updatedTeam = await teamsAPI.updateMemberRole(teamId, userId, role);
      set({ currentTeam: updatedTeam, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to update member role',
      });
      throw error;
    }
  },

  removeMember: async (teamId: string, userId: string) => {
    set({ isLoading: true, error: null });
    try {
      await teamsAPI.removeMember(teamId, userId);
      // Refresh team data
      await get().fetchTeam(teamId);
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to remove member',
      });
      throw error;
    }
  },

  clearError: () => set({ error: null }),

  reset: () =>
    set({
      teams: [],
      currentTeam: null,
      isLoading: false,
      error: null,
    }),
}));
