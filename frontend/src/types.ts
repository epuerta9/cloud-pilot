export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  structuredContent?: StructuredContent;
  requiresConfirmation?: boolean;
  confirmationData?: ConfirmationData;
  isConfirmationResponse?: boolean;
}

export interface ConfirmationData {
  flow_id?: string;
  terraform_json?: TerraformPlanJson;
  plan_output?: string;
  question?: string;
  status?: string;
  type?: string;
}

export interface TerraformPlanJson {
  format_version?: string;
  terraform_version?: string;
  planned_values?: any;
  configuration?: any;
  errored?: boolean;
  complete?: boolean;
  applyable?: boolean;
  timestamp?: string;
  root_module?: any;
  resource_changes?: Array<{
    address?: string;
    mode?: string;
    type?: string;
    name?: string;
    provider_name?: string;
    change?: {
      actions?: string[];
      before?: any;
      after?: any;
    };
  }>;
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