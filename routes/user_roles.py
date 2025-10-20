from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from middlewares.auth import get_current_user
from crud import user_roles as user_roles_crud
from schemas.user_roles import UserRoleCreate, UserRoleResponse

router = APIRouter()


@router.post("/users/roles", response_model=UserRoleResponse)
def add_role_to_user(
    role: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    role.user_id = current_user.id
    return user_roles_crud.create_user_role(db, role)


@router.get("/users/roles", response_model=List[UserRoleResponse])
def list_user_roles(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return user_roles_crud.get_roles_for_user(db, current_user.id)


@router.delete("/roles/{role_id}")
def remove_role(role_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Deleting a role requires ownership or admin — here we check ownership via role lookup
    db_role = user_roles_crud.get_user_role(db, role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    if db_role.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to remove this role")
    user_roles_crud.delete_user_role(db, role_id)
    return {"message": "Role removed"}
