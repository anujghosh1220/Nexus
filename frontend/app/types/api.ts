export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  avatar_url?: string;
  is_active: boolean;
  is_verified: boolean;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface Membership {
  id: string;
  organization_id: string;
  user_id: string;
  role: "OWNER" | "ADMIN" | "MANAGER" | "MEMBER" | "VIEWER";
  status: "PENDING" | "ACTIVE" | "INACTIVE";
  invited_at: string;
  joined_at?: string;
  created_at: string;
  updated_at: string;
  user?: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}

export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  last_used_at?: string;
  revoked_at?: string;
  created_at: string;
  key?: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface File {
  id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  url: string;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: "ACTIVE" | "ARCHIVED" | "DRAFT";
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: "TODO" | "IN_PROGRESS" | "REVIEW" | "DONE";
  priority: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
  assignee_id?: string;
  project_id: string;
  created_at: string;
  updated_at: string;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  user_id?: string;
  ip_address?: string;
  user_agent?: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface AuthError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}
