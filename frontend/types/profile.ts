export type EducationItem = {
  school?: { name?: string | null } | null;
  degrees?: string[];
  majors?: string[];
};

export type ExperienceItem = {
  company?: { name?: string | null } | null;
  title?: { name?: string | null } | null;
  start_date?: string | null;
  end_date?: string | null;
};

export type Profile = {
  id: number;
  full_name: string;
  linkedin_url: string | null;
  industry: string | null;
  job_title: string | null;
  job_company_name: string | null;
  location_name: string | null;
  summary: string | null;
  skills: string[];
  education: EducationItem[];
  experience: ExperienceItem[];
};

export type SearchResponse = {
  items: Profile[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type FilterOptions = {
  skills: string[];
  job_titles: string[];
};
