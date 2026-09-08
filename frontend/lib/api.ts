import type { FilterOptions, SearchResponse } from "@/types/profile";

const API_BASE_URL = "/api/v1";

export type SearchParams = {
  q?: string;
  skill?: string;
  jobTitle?: string;
  page?: number;
};

export async function searchProfiles(
  params: SearchParams
): Promise<SearchResponse> {
  const search = new URLSearchParams();

  if (params.q?.trim()) {
    search.set("q", params.q.trim());
  }

  if (params.skill?.trim()) {
    search.append("skill", params.skill.trim());
  }

  if (params.jobTitle?.trim()) {
    search.set("job_title", params.jobTitle.trim());
  }

  search.set("page", String(params.page ?? 1));
  search.set("page_size", "12");

  const response = await fetch(
    `${API_BASE_URL}/profiles/search?${search.toString()}`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      `Could not load search results. Status: ${response.status}`
    );
  }

  return response.json();
}

export async function getFilterOptions(): Promise<FilterOptions> {
  const response = await fetch(
    `${API_BASE_URL}/profiles/filters`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      `Could not load filter options. Status: ${response.status}`
    );
  }

  return response.json();
}
