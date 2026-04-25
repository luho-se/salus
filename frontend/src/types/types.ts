export type ProjectStep = 'INITIAL_PROMPT' | 'INITIAL_QUESTIONS' | 'DIAGNOSIS';

export interface Project {
  id: number;
  title: string;
  initialPrompt: string | null;
  step: ProjectStep;
  updatedAt: string;
  createdAt: string;
}

export interface Question {
  id: number;
  projectId: number;
  question: string;
  inputType: string;
  inputUnit: string | null;
  inputMin: number | null;
  inputMax: number | null;
  createdAt: string;
}

export interface Answer {
  id: number;
  projectId: number;
  questionId: number;
  answer: string | null;
  updatedAt: string;
  createdAt: string;
}

export interface QuestionWithAnswer extends Question {
  answer: Answer | null;
}

export interface DiagnosisItem {
  id: number;
  diagnosisId: number;
  title: string;
  motivation: string;
  recommendations: string;
}

export interface DiagnosisSentenceWeight {
  id: number;
  diagnosisId: number;
  questionId: number;
  answer: string;
  sentenceWeight: number | null;
}

export interface Diagnosis {
  id: number;
  projectId: number;
  createdAt: string;
  items: DiagnosisItem[];
  sentenceWeights: DiagnosisSentenceWeight[];
}

export interface ProjectDetail extends Project {
  questions: QuestionWithAnswer[];
  diagnosis: Diagnosis | null;
}
