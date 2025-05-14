// Task model for tracking tasks and their completion status

export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: Date;
  completedAt?: Date;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  userId?: string; // For multi-user support
}

// In-memory storage for tasks (replace with database in production)
class TaskStore {
  private tasks: Map<string, Task> = new Map();

  // Get all tasks
  getAllTasks(): Task[] {
    return Array.from(this.tasks.values());
  }

  // Get tasks by user ID
  getTasksByUser(userId: string): Task[] {
    return this.getAllTasks().filter(task => task.userId === userId);
  }

  // Get task by ID
  getTaskById(id: string): Task | undefined {
    return this.tasks.get(id);
  }

  // Create a new task
  createTask(task: Omit<Task, 'id' | 'createdAt'>): Task {
    const id = Date.now().toString();
    const newTask: Task = {
      id,
      ...task,
      completed: task.completed || false,
      createdAt: new Date(),
    };
    this.tasks.set(id, newTask);
    return newTask;
  }

  // Update a task
  updateTask(id: string, updates: Partial<Task>): Task | undefined {
    const task = this.tasks.get(id);
    if (!task) return undefined;

    // If marking as completed, set completedAt
    if (updates.completed && !task.completed) {
      updates.completedAt = new Date();
    }
    
    // If marking as not completed, remove completedAt
    if (updates.completed === false && task.completed) {
      updates.completedAt = undefined;
    }

    const updatedTask = { ...task, ...updates };
    this.tasks.set(id, updatedTask);
    return updatedTask;
  }

  // Delete a task
  deleteTask(id: string): boolean {
    return this.tasks.delete(id);
  }

  // Mark a task as complete
  completeTask(id: string): Task | undefined {
    return this.updateTask(id, { completed: true });
  }

  // Mark a task as incomplete
  uncompleteTask(id: string): Task | undefined {
    return this.updateTask(id, { completed: false });
  }
}

// Export a singleton instance
export const taskStore = new TaskStore();
