from pydantic import BaseModel,ConfigDict,Field

class ProfileItem(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    evidence: str = Field(min_length=1)

class ResumeProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skills: list[ProfileItem]
    projects: list[ProfileItem]

def check_profile_evidence(profile: ResumeProfile,source_text: str) -> None:
    for item in profile.skills + profile.projects:
        if item.evidence not in source_text:
            raise ValueError(item.name)