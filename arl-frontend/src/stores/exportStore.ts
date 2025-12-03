import { create } from 'zustand';
import type { ExportJob, ExportRequest } from '@/types/export';
import { exportsAPI } from '@/api/exports';

interface ExportState {
  exports: ExportJob[];
  currentExport: ExportJob | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  createExport: (data: ExportRequest) => Promise<ExportJob>;
  getExport: (exportId: string) => Promise<void>;
  fetchExports: (projectId?: string) => Promise<void>;
  downloadExport: (exportId: string) => Promise<void>;
  pollExportStatus: (exportId: string) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

export const useExportStore = create<ExportState>((set, get) => ({
  exports: [],
  currentExport: null,
  isLoading: false,
  error: null,

  createExport: async (data: ExportRequest) => {
    set({ isLoading: true, error: null });
    try {
      const exportJob = await exportsAPI.createExport(data);
      set((state) => ({
        exports: [exportJob, ...state.exports],
        currentExport: exportJob,
        isLoading: false,
      }));

      // Start polling for status
      get().pollExportStatus(exportJob.id);

      return exportJob;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to create export',
      });
      throw error;
    }
  },

  getExport: async (exportId: string) => {
    set({ isLoading: true, error: null });
    try {
      const exportJob = await exportsAPI.getExport(exportId);
      set((state) => ({
        exports: state.exports.map((e) => (e.id === exportId ? exportJob : e)),
        currentExport: exportJob,
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch export',
      });
    }
  },

  fetchExports: async (projectId?: string) => {
    set({ isLoading: true, error: null });
    try {
      const exports = await exportsAPI.listExports(projectId);
      set({ exports, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch exports',
      });
    }
  },

  downloadExport: async (exportId: string) => {
    try {
      await exportsAPI.downloadExport(exportId);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to download export',
      });
      throw error;
    }
  },

  pollExportStatus: async (exportId: string) => {
    const poll = async () => {
      try {
        const exportJob = await exportsAPI.getExport(exportId);
        set((state) => ({
          exports: state.exports.map((e) => (e.id === exportId ? exportJob : e)),
          currentExport: state.currentExport?.id === exportId ? exportJob : state.currentExport,
        }));

        // Continue polling if still processing
        if (exportJob.status === 'pending' || exportJob.status === 'processing') {
          setTimeout(poll, 2000);
        }
      } catch (error) {
        console.error('Error polling export status:', error);
      }
    };

    poll();
  },

  clearError: () => set({ error: null }),

  reset: () =>
    set({
      exports: [],
      currentExport: null,
      isLoading: false,
      error: null,
    }),
}));
