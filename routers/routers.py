from fastapi import APIRouter

from .projects.router import router as projects
from .floors.rotuer import router as floors
from .rows.router import router as rows
from .seats.router import router as seats
from .seat_category.router import router as seat_category
from .seat_status.router import router as seat_status
from .section.router import router as section

# from .bulk.router import router as bulk
from .booked.rotuer import router as booking
from .payments.router import router as payments
from .tikets.router import router as tikets

from .user.router import router as user

routers = APIRouter()

routers.include_router(projects)
routers.include_router(floors)
routers.include_router(rows)
routers.include_router(seats)
routers.include_router(seat_category)
routers.include_router(seat_status)
routers.include_router(section)

# routers.include_router(bulk)
routers.include_router(booking)
routers.include_router(payments)
routers.include_router(tikets)

routers.include_router(user)

