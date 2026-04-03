import json
import os
from typing import List, Optional
from app.models.schemas import SearchRequest, MatchedCollege, College, Branch

# ── Load college data once at startup ────────────────────────────────────────

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/colleges.json")

def _load_colleges() -> List[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

_COLLEGES: List[dict] = _load_colleges()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_cutoff(branch: dict, exam: str, category: str) -> Optional[int]:
    """Safely retrieve a cutoff rank for a given exam and category."""
    return branch.get("cutoffs", {}).get(exam, {}).get(category)


def _branch_eligible(
    branch: dict,
    jee_rank: Optional[int],
    wbjee_rank: Optional[int],
    class12_percent: float,
    category: str,
    branch_filter: str,
) -> bool:
    """Return True if the student is eligible for this branch."""

    # Class 12 minimum check
    if class12_percent < branch.get("min_class12_percentage", 0):
        return False

    # Branch name filter
    if branch_filter != "Any Branch" and branch.get("name") != branch_filter:
        return False

    # Rank check — eligible if rank ≤ cutoff for at least one exam
    jee_cutoff   = _get_cutoff(branch, "JEE_Main", category)
    wbjee_cutoff = _get_cutoff(branch, "WBJEE", category)

    jee_ok   = (jee_rank   is not None) and (jee_cutoff   is not None) and (jee_rank   <= jee_cutoff)
    wbjee_ok = (wbjee_rank is not None) and (wbjee_cutoff is not None) and (wbjee_rank <= wbjee_cutoff)

    return jee_ok or wbjee_ok


def _college_passes_filters(college: dict, req: SearchRequest) -> bool:
    """Return True if college matches the non-rank preference filters."""

    if req.state != "Both" and college.get("state") != req.state:
        return False

    if req.college_type != "Any" and college.get("type") != req.college_type:
        return False

    if req.affiliation != "Any" and college.get("affiliation") != req.affiliation:
        return False

    if req.fees_range != "Any" and college.get("fees_range") != req.fees_range:
        return False

    return True


# ── Main matcher ──────────────────────────────────────────────────────────────

def match_colleges(req: SearchRequest) -> List[MatchedCollege]:
    """
    Core matching function.
    1. Filter colleges by preference (state, type, affiliation, fees).
    2. For each college, find branches the student is eligible for.
    3. Discard colleges with 0 matched branches.
    4. Attach a match_score and sort.
    """

    results: List[MatchedCollege] = []

    for raw in _COLLEGES:
        # Step 1 — preference filters
        if not _college_passes_filters(raw, req):
            continue

        # Step 2 — branch matching
        matched_branches = [
            b for b in raw.get("branches", [])
            if _branch_eligible(
                b,
                req.jee_rank,
                req.wbjee_rank,
                req.class12_percent,
                req.category,
                req.branch,
            )
        ]

        # Step 3 — skip if no branches matched
        if not matched_branches:
            continue

        # Step 4 — build response object
        total_branches = len(raw.get("branches", [])) or 1
        match_score    = round((len(matched_branches) / total_branches) * 100, 1)

        results.append(
            MatchedCollege(
                college=College(**raw),
                matched_branches=[Branch(**b) for b in matched_branches],
                match_score=match_score,
            )
        )

    # ── Sorting ───────────────────────────────────────────────────────────────
    if req.sort_by == "rank":
        results.sort(key=lambda r: r.college.nirf_ranking or 9999)
    elif req.sort_by == "name":
        results.sort(key=lambda r: r.college.name)
    elif req.sort_by == "branches":
        results.sort(key=lambda r: len(r.matched_branches), reverse=True)
    elif req.sort_by == "match_score":
        results.sort(key=lambda r: r.match_score, reverse=True)

    return results


def get_college_by_id(college_id: int) -> Optional[College]:
    """Find and return a single college by ID."""
    for raw in _COLLEGES:
        if raw.get("id") == college_id:
            return College(**raw)
    return None