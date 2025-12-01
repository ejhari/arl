import { create } from 'zustand';
import { canvasAPI } from '@/api/canvas';
import type {
  Project,
  Cell,
  CreateProjectData,
  UpdateProjectData,
  CreateCellData,
  UpdateCellData,
} from '@/types/canvas';

interface CanvasState {
  // Projects
  projects: Project[];
  currentProject: Project | null;
  projectsLoading: boolean;

  // Cells
  cells: Cell[];
  selectedCellId: string | null;
  cellsLoading: boolean;

  // Errors
  error: string | null;

  // Project actions
  loadProjects: () => Promise<void>;
  loadProject: (projectId: string) => Promise<void>;
  createProject: (data: CreateProjectData) => Promise<Project>;
  updateProject: (projectId: string, data: UpdateProjectData) => Promise<void>;
  deleteProject: (projectId: string) => Promise<void>;
  setCurrentProject: (project: Project | null) => void;

  // Cell actions
  loadCells: (projectId: string) => Promise<void>;
  createCell: (data: CreateCellData) => Promise<Cell>;
  updateCell: (cellId: string, data: UpdateCellData) => Promise<void>;
  deleteCell: (cellId: string) => Promise<void>;
  reorderCells: (cellId: string, newPosition: number) => Promise<void>;
  selectCell: (cellId: string | null) => void;

  // Real-time updates
  addCell: (cell: Cell) => void;
  updateCellLocal: (cellId: string, updates: Partial<Cell>) => void;
  removeCellLocal: (cellId: string) => void;

  // Utility
  clearError: () => void;
  reset: () => void;
}

export const useCanvasStore = create<CanvasState>((set, get) => ({
  // Initial state
  projects: [],
  currentProject: null,
  projectsLoading: false,
  cells: [],
  selectedCellId: null,
  cellsLoading: false,
  error: null,

  // Project actions
  loadProjects: async () => {
    set({ projectsLoading: true, error: null });
    try {
      const projects = await canvasAPI.listProjects();
      set({ projects, projectsLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load projects',
        projectsLoading: false,
      });
    }
  },

  loadProject: async (projectId: string) => {
    set({ projectsLoading: true, error: null });
    try {
      const project = await canvasAPI.getProject(projectId);
      set({
        currentProject: project,
        cells: project.cells.sort((a, b) => a.position - b.position),
        projectsLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load project',
        projectsLoading: false,
      });
    }
  },

  createProject: async (data: CreateProjectData) => {
    set({ error: null });
    try {
      const project = await canvasAPI.createProject(data);
      set((state) => ({
        projects: [project, ...state.projects],
      }));
      return project;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to create project';
      set({ error: errorMsg });
      throw error;
    }
  },

  updateProject: async (projectId: string, data: UpdateProjectData) => {
    set({ error: null });
    try {
      const updated = await canvasAPI.updateProject(projectId, data);
      set((state) => ({
        projects: state.projects.map((p) => (p.id === projectId ? updated : p)),
        currentProject: state.currentProject?.id === projectId ? updated : state.currentProject,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update project',
      });
      throw error;
    }
  },

  deleteProject: async (projectId: string) => {
    set({ error: null });
    try {
      await canvasAPI.deleteProject(projectId);
      set((state) => ({
        projects: state.projects.filter((p) => p.id !== projectId),
        currentProject: state.currentProject?.id === projectId ? null : state.currentProject,
        cells: state.currentProject?.id === projectId ? [] : state.cells,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete project',
      });
      throw error;
    }
  },

  setCurrentProject: (project: Project | null) => {
    set({ currentProject: project });
  },

  // Cell actions
  loadCells: async (projectId: string) => {
    set({ cellsLoading: true, error: null });
    try {
      const cells = await canvasAPI.listCells(projectId);
      set({
        cells: cells.sort((a, b) => a.position - b.position),
        cellsLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load cells',
        cellsLoading: false,
      });
    }
  },

  createCell: async (data: CreateCellData) => {
    set({ error: null });
    try {
      const cell = await canvasAPI.createCell(data);
      set((state) => ({
        cells: [...state.cells, cell].sort((a, b) => a.position - b.position),
      }));
      return cell;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to create cell';
      set({ error: errorMsg });
      throw error;
    }
  },

  updateCell: async (cellId: string, data: UpdateCellData) => {
    set({ error: null });
    try {
      const updated = await canvasAPI.updateCell(cellId, data);
      set((state) => ({
        cells: state.cells.map((c) => (c.id === cellId ? updated : c)),
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update cell',
      });
      throw error;
    }
  },

  deleteCell: async (cellId: string) => {
    set({ error: null });
    try {
      await canvasAPI.deleteCell(cellId);
      set((state) => ({
        cells: state.cells.filter((c) => c.id !== cellId),
        selectedCellId: state.selectedCellId === cellId ? null : state.selectedCellId,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete cell',
      });
      throw error;
    }
  },

  reorderCells: async (cellId: string, newPosition: number) => {
    set({ error: null });
    try {
      // Optimistic update
      const cells = [...get().cells];
      const cellIndex = cells.findIndex((c) => c.id === cellId);
      if (cellIndex === -1) return;

      const [movedCell] = cells.splice(cellIndex, 1);
      cells.splice(newPosition, 0, movedCell);

      // Update positions
      const updatedCells = cells.map((cell, index) => ({
        ...cell,
        position: index,
      }));

      set({ cells: updatedCells });

      // Update on server
      await canvasAPI.updateCell(cellId, { position: newPosition });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to reorder cells',
      });
      // Reload cells on error
      if (get().currentProject) {
        get().loadCells(get().currentProject!.id);
      }
    }
  },

  selectCell: (cellId: string | null) => {
    set({ selectedCellId: cellId });
  },

  // Real-time updates
  addCell: (cell: Cell) => {
    set((state) => {
      // Don't add if already exists
      if (state.cells.some((c) => c.id === cell.id)) {
        return state;
      }
      return {
        cells: [...state.cells, cell].sort((a, b) => a.position - b.position),
      };
    });
  },

  updateCellLocal: (cellId: string, updates: Partial<Cell>) => {
    set((state) => ({
      cells: state.cells.map((c) => (c.id === cellId ? { ...c, ...updates } : c)),
    }));
  },

  removeCellLocal: (cellId: string) => {
    set((state) => ({
      cells: state.cells.filter((c) => c.id !== cellId),
      selectedCellId: state.selectedCellId === cellId ? null : state.selectedCellId,
    }));
  },

  // Utility
  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set({
      projects: [],
      currentProject: null,
      projectsLoading: false,
      cells: [],
      selectedCellId: null,
      cellsLoading: false,
      error: null,
    });
  },
}));
