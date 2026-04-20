from fastapi import APIRouter, Header, HTTPException
from app.services.user_service import get_or_create_user

router = APIRouter()

PLANS = {
    "free": {"requestsPerDay": 3},
    "pro": {"requestsPerDay": 50},
    "premium": {"requestsPerDay": 200},
}


@router.get("/me")
async def get_me(x_user_id: str = Header()):
    if not x_user_id:
        raise HTTPException(status_code=400, detail="Missing user id")

    user = get_or_create_user(x_user_id)
    plan = PLANS[user["plan"]]

    return {
        "id": user["id"],
        "email": user["email"],
        "plan": user["plan"],
        "requests_used": user["requests_used"],
        "requests_limit": plan["requestsPerDay"],
    }