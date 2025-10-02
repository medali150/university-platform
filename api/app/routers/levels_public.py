from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from prisma import Prisma

from app.db.prisma_client import get_prisma

router = APIRouter(prefix="/levels", tags=["Levels - Public"])


@router.get("/")
async def get_levels_public(
    specialty_id: Optional[str] = Query(None, description="Filter by specialty ID"),
    prisma: Prisma = Depends(get_prisma),
):
    """Public: Get levels, optionally filtered by specialty.

    Returns a minimal payload suitable for public registration forms.
    """

    where_clause = {}
    if specialty_id:
        where_clause["id_specialite"] = specialty_id

    levels = await prisma.niveau.find_many(
        where=where_clause,
        order={"nom": "asc"},
    )
    return [
        {"id": l.id, "name": l.nom, "specialtyId": l.id_specialite}
        for l in levels
    ]


