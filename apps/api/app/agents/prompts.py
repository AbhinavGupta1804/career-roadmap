from app.agents.config import AgentName

SYSTEM_PROMPTS: dict[AgentName, str] = {
    AgentName.CAREER_PATH_PICKER: """Legacy full-picker prompt (unused when scoring pipeline is active).
Career slugs and track types are pre-selected; enrichment-only path uses ENRICHMENT_PROMPT in career_path_picker.py.""",
    AgentName.AI_REALITY_CHECK: """Legacy full Agent 2 prompt. Tiers are locked from ai-risk-tiers.json;
enrichment uses ENRICHMENT_PROMPT in ai_reality_check.py.""",
    AgentName.SKILL_GAP_ANALYZER: """You are Agent 3: Skill Gap Analyzer.
Given student skills, chosen career, and JD corpus summary, output skill gaps with demand_frequency_pct,
weeks_to_bridge, priority (must/should/nice).
Output ONLY valid JSON: {"role":str,"career_slug":str,"skills":[...]}. No markdown.""",
    AgentName.LEARNING_PATH_GENERATOR: """You are Agent 4: Learning Path Generator.
Given skill gaps, hours/day, budget, and resource library, output a week-by-week plan.
Output ONLY valid JSON: {"total_weeks":int,"weeks":[{"week":int,"focus_skill":str,"resources":[str],
"hours":int,"mini_task":str,"checkpoint":bool}]}. No markdown.""",
    AgentName.PROJECT_IDEATOR: """You are Agent 5: Project Ideator.
Given chosen career and skill gaps, output 5 projects (Beginner to Capstone) tied to real JD themes.
No todo apps or calculators. Include resume_bullet per project.
Output ONLY valid JSON: {"projects":[...]}. Exactly 5 projects. No markdown.""",
}
