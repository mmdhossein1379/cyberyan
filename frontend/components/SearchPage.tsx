"use client";

import { FormEvent, useEffect, useState } from "react";

import { getFilterOptions, searchProfiles } from "@/lib/api";
import type { FilterOptions, SearchResponse } from "@/types/profile";
import { ProfileCard } from "./ProfileCard";

const emptyResult: SearchResponse = {
  items: [],
  total: 0,
  page: 1,
  page_size: 12,
  pages: 0,
};

export function SearchPage() {
  const [query, setQuery] = useState("");
  const [skill, setSkill] = useState("");
  const [jobTitle, setJobTitle] = useState("");

  const [result, setResult] =
    useState<SearchResponse>(emptyResult);

  const [options, setOptions] =
    useState<FilterOptions>({
      skills: [],
      job_titles: [],
    });

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  async function load(page = 1) {
    setLoading(true);
    setError(null);

    try {
      const data = await searchProfiles({
        q: query.trim() || undefined,
        skill: skill.trim() || undefined,
        jobTitle: jobTitle.trim() || undefined,
        page,
      });

      setResult(data);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unexpected error."
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    async function initialize() {
      try {
        const [
          filterOptions,
          firstPage,
        ] = await Promise.all([
          getFilterOptions(),
          searchProfiles({
            page: 1,
          }),
        ]);

        setOptions(filterOptions);
        setResult(firstPage);

      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unexpected error."
        );
      } finally {
        setLoading(false);
      }
    }

    initialize();
  }, []);


  function submit(
    event: FormEvent
  ) {
    event.preventDefault();

    void load(1);
  }


  function reset() {
    setQuery("");
    setSkill("");
    setJobTitle("");

    setLoading(true);

    searchProfiles({
      page: 1,
    })
      .then(setResult)
      .catch((err: unknown) =>
        setError(
          err instanceof Error
            ? err.message
            : "Unexpected error."
        )
      )
      .finally(() =>
        setLoading(false)
      );
  }


  return (
    <main className="shell">

      <section className="hero">
        <div>
          <p className="eyebrow">
            Candidate Search
          </p>

          <h1>
            LinkedIn profile search
          </h1>

          <p>
            Search profiles by keyword,
            skill, and current job title.
          </p>
        </div>


        <div className="stat">
          <strong>
            {result.total}
          </strong>

          <span>
            matching profiles
          </span>
        </div>
      </section>



      <form
        className="searchPanel"
        onSubmit={submit}
      >

        <label className="field fieldWide">

          <span>
            Keyword
          </span>

          <input
            value={query}
            onChange={(event) =>
              setQuery(
                event.target.value
              )
            }
            placeholder="e.g. python, recruiter, aviation"
          />

        </label>



        <label className="field">

          <span>
            Skill
          </span>

          <input
            list="skills"
            value={skill}
            onChange={(event) =>
              setSkill(
                event.target.value
              )
            }
            placeholder="e.g. python"
          />


          <datalist id="skills">

            {options.skills.map(
              (value) => (
                <option
                  key={value}
                  value={value}
                />
              )
            )}

          </datalist>

        </label>




        <label className="field">

          <span>
            Job title
          </span>


          <input
            list="job-titles"
            value={jobTitle}
            onChange={(event) =>
              setJobTitle(
                event.target.value
              )
            }
            placeholder="e.g. data analyst"
          />


          <datalist id="job-titles">

            {options.job_titles.map(
              (value) => (
                <option
                  key={value}
                  value={value}
                />
              )
            )}

          </datalist>

        </label>



        <div className="actions">

          <button
            type="submit"
            disabled={loading}
          >
            Search
          </button>


          <button
            className="secondary"
            type="button"
            onClick={reset}
            disabled={loading}
          >
            Reset
          </button>

        </div>


      </form>




      {error && (
        <div className="error">
          {error}
        </div>
      )}



      <section className="resultHeader">

        <div>

          <h2>
            Results
          </h2>


          <p>
            {
              loading
                ? "Loading…"
                : `${result.total} profiles found`
            }
          </p>

        </div>

      </section>




      {!loading &&
        !error &&
        result.items.length === 0 && (

        <div className="empty">
          No profiles match the current search.
        </div>

      )}



      <section className="grid">

        {
          result.items.map(
            (profile) => (
              <ProfileCard
                key={profile.id}
                profile={profile}
              />
            )
          )
        }

      </section>




      {result.pages > 1 && (

        <nav
          className="pagination"
          aria-label="Pagination"
        >

          <button
            className="secondary"
            disabled={
              loading ||
              result.page <= 1
            }
            onClick={() =>
              void load(
                result.page - 1
              )
            }
          >
            Previous
          </button>



          <span>
            Page {result.page} of {result.pages}
          </span>



          <button
            className="secondary"
            disabled={
              loading ||
              result.page >= result.pages
            }
            onClick={() =>
              void load(
                result.page + 1
              )
            }
          >
            Next
          </button>


        </nav>

      )}

    </main>
  );
}
