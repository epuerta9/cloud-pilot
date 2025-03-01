export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  structuredContent?: StructuredContent;
  requiresConfirmation?: boolean;
  confirmationData?: any;
  isConfirmationResponse?: boolean;
}

// Define a specific type for table rows
export interface TableRow {
  [key: string]: string;
}

export interface ContentSection {
  title?: string;
  type?: string;
  content: string | string[] | React.ReactNode | TableRow[];
  metadata?: {
    level?: number;
    language?: string;
    [key: string]: any;
  };
}

export interface StructuredContent {
  title: string;
  sections: ContentSection[];
} 