import type { Profile } from "@/types/profile";

function normalizeLinkedInUrl(value: string | null) {
  if (!value) return null;
  return value.startsWith("http") ? value : `https://${value}`;
}

export function ProfileCard({ profile }: { profile: Profile }) {
  const linkedin = normalizeLinkedInUrl(profile.linkedin_url);
  const education = profile.education.find((item) => item.school?.name);

  return (
    <article className="card">
      <div className="cardHeader">
        <div>
          <h2>{profile.full_name}</h2>
          <p className="role">
            {profile.job_title ?? "Role not specified"}
            {profile.job_company_name ? ` · ${profile.job_company_name}` : ""}
          </p>
        </div>
        {linkedin && (
          <a className="linkedinLink" href={linkedin} target="_blank" rel="noreferrer">
            LinkedIn ↗
          </a>
        )}
      </div>

      <div className="metaRow">
        {profile.location_name && <span>{profile.location_name}</span>}
        {profile.industry && <span>{profile.industry}</span>}
      </div>

      {profile.summary && <p className="summary">{profile.summary}</p>}

      {education?.school?.name && (
        <p className="education"><strong>Education:</strong> {education.school.name}</p>
      )}

      <div className="skills">
        {profile.skills.slice(0, 8).map((skill) => (
          <span key={skill}>{skill}</span>
        ))}
      </div>
    </article>
  );
}
