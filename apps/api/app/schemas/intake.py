from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl, field_validator


class YearOfStudy(str, Enum):
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"
    FOURTH = "4th"
    DROPOUT = "Dropout"
    GAP_YEAR = "Gap year"


class TechStream(str, Enum):
    """Degree branch / stream (engineering, commerce, business, etc.)."""

    CS = "CS"
    IT = "IT"
    ECE = "ECE"
    EE = "EE"
    MECHANICAL = "Mechanical"
    CIVIL = "Civil"
    COMMERCE = "Commerce"
    BBA = "BBA"


class CollegeTier(str, Enum):
    TIER_1 = "Tier 1 (IIT/NIT/IIIT)"
    TIER_2 = "Tier 2"
    TIER_3 = "Tier 3"


class CgpaBand(str, Enum):
    BELOW_6_5 = "<6.5"
    BAND_6_5_7_5 = "6.5–7.5"
    BAND_7_5_8_5 = "7.5–8.5"
    ABOVE_8_5 = "8.5+"


class RelocationPreference(str, Enum):
    YES = "Yes"
    NO = "No"
    REMOTE = "Open to remote"


class HoursPerDay(str, Enum):
    ONE = "1hr"
    TWO_TO_THREE = "2–3hr"
    FOUR_PLUS = "4+hr"


class BudgetInr(str, Enum):
    ZERO = "0"
    LOW = "0–2k"
    MID = "2–10k"
    HIGH = "10k+"


class InterestArea(str, Enum):
    MACHINE_LEARNING = "Machine Learning"
    DATA_SCIENCE = "Data Science"
    UI_UX_DESIGN = "UI/UX Design"
    WEB_DEV = "Web Dev"
    MOBILE_DEV = "Mobile Dev"
    CYBERSECURITY = "Cybersecurity"
    CLOUD_DEVOPS = "Cloud/DevOps"
    PRODUCT_MANAGEMENT = "Product Management"
    GAME_DEV = "Game Dev"
    HARDWARE = "Hardware"
    ROBOTICS = "Robotics"
    BUSINESS_ANALYST = "Business Analyst"
    FINANCE_ACCOUNTING = "Finance & Accounting"
    DIGITAL_MARKETING = "Digital Marketing"
    OTHER = "Other"


class SkillRating(str, Enum):
    HEARD_OF = "heard of it"
    WITH_HELP = "can use with help"
    SOLO = "can build solo"


class PrimaryGoal(str, Enum):
    FIRST_JOB = "First job"
    INTERNSHIP = "Internship"
    HIGHER_STUDIES = "Higher studies"
    STARTUP = "Startup"
    FREELANCING = "Freelancing"


class TargetSalaryBand(str, Enum):
    BAND_3_6 = "₹3–6 LPA"
    BAND_6_12 = "₹6–12 LPA"
    BAND_12_PLUS = "₹12+ LPA"


class TimelineToJob(str, Enum):
    THREE_MONTHS = "3 months"
    SIX_MONTHS = "6 months"
    TWELVE_MONTHS = "12 months"
    TWO_PLUS_YEARS = "2+ years"


LikertScore = Annotated[int, Field(ge=1, le=5)]


class ProfileBasics(BaseModel):
    year_of_study: YearOfStudy
    stream: TechStream
    college_tier: CollegeTier
    cgpa_band: CgpaBand
    city: str = Field(min_length=1, max_length=100)
    relocation: RelocationPreference
    hours_per_day: HoursPerDay
    budget_inr: BudgetInr


class SelfAssessment(BaseModel):
    coding_comfort: LikertScore
    math_logic_comfort: LikertScore
    communication_comfort: LikertScore
    design_visual_comfort: LikertScore
    people_sales_comfort: LikertScore
    detail_patience: LikertScore
    interest_bias: list[InterestArea] = Field(min_length=1, max_length=3)
    commitment_slider: Annotated[int, Field(ge=0, le=10)]

    @field_validator("interest_bias")
    @classmethod
    def unique_interests(cls, values: list[InterestArea]) -> list[InterestArea]:
        if len(values) != len(set(values)):
            raise ValueError("interest_bias entries must be unique")
        return values


class StudentSkill(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    rating: SkillRating


class SkillsAndGoals(BaseModel):
    skills: list[StudentSkill] = Field(default_factory=list)
    projects_text: str | None = Field(default=None, max_length=2000)
    github_url: HttpUrl | None = None
    has_internship: bool
    internship_brief: str | None = Field(default=None, max_length=500)
    primary_goal: PrimaryGoal
    target_salary_band: TargetSalaryBand
    timeline_to_job: TimelineToJob
    dream_companies: list[str] = Field(default_factory=list, max_length=3)

    @field_validator("dream_companies")
    @classmethod
    def trim_companies(cls, values: list[str]) -> list[str]:
        return [company.strip() for company in values if company.strip()]


class IntakeForm(BaseModel):
    profile: ProfileBasics
    self_assessment: SelfAssessment
    skills_and_goals: SkillsAndGoals
