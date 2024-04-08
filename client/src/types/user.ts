export interface User {
  chapter: string | null;
  department: string | null;
  email: string;
  gmail: string;
  leader: string | null;
  name: string;
  phone: string;
  team: string | null;
  uuid: string;
}

export interface ProfileFormValues
  extends Pick<Partial<User>, 'gmail' | 'name' | 'phone'> {}
