from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ── Request body sent by the React frontend ──────────────────────────────────

class SearchRequest(BaseModel):
    jee_rank:        Optional[int]   = Field(None,  gt=0, description="JEE Main rank")
    wbjee_rank:      Optional[int]   = Field(None,  gt=0, description="WBJEE rank")
    class12_percent: float           = Field(...,   ge=0, le=100, description="Class 12 percentage")
    category:        str             = Field("General", description="General / OBC / SC / ST / EWS")
    state:           str             = Field("Both",    description="Both / Jharkhand / West Bengal")
    branch:          str             = Field("Any Branch")
    college_type:    str             = Field("Any",     description="Any / Government / Private / Deemed")
    affiliation:     str             = Field("Any",     description="Any / Autonomous / University Affiliated")
    fees_range:      str             = Field("Any",     description="Any / Low / Medium / High")
    sort_by:         str             = Field("rank",    description="rank / name / branches")

    class Config:
        # Allow camelCase from frontend to map to snake_case fields
        populate_by_name = True


# ── Individual cutoff entry ───────────────────────────────────────────────────

class CategoryCutoffs(BaseModel):
    General: Optional[int] = None
    OBC:     Optional[int] = None
    SC:      Optional[int] = None
    ST:      Optional[int] = None
    EWS:     Optional[int] = None


class BranchCutoffs(BaseModel):
    JEE_Main: Optional[CategoryCutoffs] = None
    WBJEE:    Optional[CategoryCutoffs] = None


# ── Branch (matched) ──────────────────────────────────────────────────────────

class Branch(BaseModel):
    name:                  str
    code:                  str
    cutoffs:               BranchCutoffs
    min_class12_percentage: float


# ── College (full) ────────────────────────────────────────────────────────────

class College(BaseModel):
    id:            int
    name:          str
    state:         str
    city:          str
    type:          str
    affiliation:   Optional[str] = None
    fees_range:    Optional[str] = None
    annual_fees_inr: Optional[int] = None
    branches:      List[Branch]
    nirf_ranking:  Optional[int] = None
    website:       Optional[str] = None
    established:   Optional[int] = None


# ── Single result item returned per matched college ───────────────────────────

class MatchedCollege(BaseModel):
    college:          College
    matched_branches: List[Branch]
    match_score:      float        # 0–100, % of branches matched


# ── Full search response ──────────────────────────────────────────────────────

class SearchResponse(BaseModel):
    total:   int
    results: List[MatchedCollege]


# ── College detail response (single college) ──────────────────────────────────

class CollegeDetailResponse(BaseModel):
    college: College