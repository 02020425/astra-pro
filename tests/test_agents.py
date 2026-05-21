import pytest
from astra_pro.agents import TutorAgent, HomeworkGraderAgent, StudyPlannerAgent


def test_tutor_agent_exists():
    agent = TutorAgent()
    assert agent.name == "tutor"
    assert "数学" in agent.subjects


def test_homework_grader_agent_exists():
    agent = HomeworkGraderAgent()
    assert agent.name == "homework_grader"


def test_study_planner_agent_exists():
    agent = StudyPlannerAgent()
    assert agent.name == "study_planner"