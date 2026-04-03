from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest, SearchResponse, CollegeDetailResponse
from app.services.matcher import match_colleges, get_college_by_id

router = APIRouter(prefix="/api", tags=["colleges"])


@router.post("/search", response_model=SearchResponse)
def search_colleges(req: SearchRequest):
    """
    Main search endpoint.

    Accepts student academic profile and preferences,
    returns list of matched colleges with eligible branches.

    At least one rank (jee_rank or wbjee_rank) must be provided.
    """
    if req.jee_rank is None and req.wbjee_rank is None:
        raise HTTPException(
            status_code=422,
            detail="At least one rank (jee_rank or wbjee_rank) must be provided."
        )

    results = match_colleges(req)

    return SearchResponse(total=len(results), results=results)


@router.get("/colleges/{college_id}", response_model=CollegeDetailResponse)
def get_college(college_id: int):
    """
    College detail endpoint.

    Returns full data for a single college by ID,
    including all branches and cutoffs.
    """
    college = get_college_by_id(college_id)

    if not college:
        raise HTTPException(status_code=404, detail=f"College with id {college_id} not found.")

    return CollegeDetailResponse(college=college)


@router.get("/health")
def health_check():
    """Simple health check — use to confirm the server is running."""
    return {"status": "ok", "message": "CollegePath API is running"}