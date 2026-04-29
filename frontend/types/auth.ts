export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  last_login: string | null;
  date_joined: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: "bearer";
  user: User;
}

export interface LoginPayload {
  identifier: string;
  password: string;
}

export interface RegisterPayload extends LoginPayload {
  username: string;
  email: string;
  full_name?: string;
}

export interface UpdateProfilePayload {
  username?: string;
  email?: string;
  full_name?: string;
}

export interface UpdatePasswordPayload {
  current_password: string;
  new_password: string;
}
