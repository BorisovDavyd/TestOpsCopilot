from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"


class StepArtifact(BaseModel):
    name: str
    path: str
    description: Optional[str] = None


class StepResult(BaseModel):
    status: StepStatus = StepStatus.queued
    summary: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    artifacts: List[StepArtifact] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory=dict)


class RunInput(BaseModel):
    requirements: Optional[str] = None
    openapi: Optional[str] = None
    model: Optional[str] = None


class RunRecord(BaseModel):
    id: str
    input: RunInput
    steps: Dict[str, StepResult]
    created_at: str
    updated_at: str


class AnalystPlan(BaseModel):
    features: List[str] = Field(default_factory=list)
    flows: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    coverage_matrix: Dict[str, List[str]] = Field(default_factory=dict)
    gaps: List[str] = Field(default_factory=list)


class ManualTestCase(BaseModel):
    title: str
    severity: str
    owner: str
    priority: str
    feature: str
    story: str
    suite: str
    tags: List[str]
    steps: List[str]
    expected: List[str]


class ManualBundle(BaseModel):
    cases: List[ManualTestCase]


class AutotestCase(BaseModel):
    name: str
    steps: List[str]
    assertions: List[str]
    target: str
    negative: bool = False


class AutotestBundle(BaseModel):
    ui: List[AutotestCase] = Field(default_factory=list)
    api: List[AutotestCase] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    type: str
    severity: str
    location: Optional[str] = None
    message: str
    suggestion: Optional[str] = None


class StandardsReport(BaseModel):
    issues: List[ValidationIssue]
    valid: bool


class OptimizationReport(BaseModel):
    duplicates: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

