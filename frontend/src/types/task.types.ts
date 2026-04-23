export interface Task {
  id: number;
  title: string;
  description: string;
  done: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskInput {
  title: string;
  description: string;
}
