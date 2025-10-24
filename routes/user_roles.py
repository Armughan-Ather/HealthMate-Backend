from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from middlewares.auth import get_current_user, get_current_user_without_role
from crud import user_roles as user_roles_crud
from schemas.user_roles import UserRoleCreate, UserRoleResponse, SwitchRoleRequest
from models.users import User
from models.user_roles import UserRole
from crud.users import create_access_token
from constants.enums import UserRoleEnum
router = APIRouter()

@router.post("/switch", status_code=200)
def switch_user_role(
    payload: SwitchRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_without_role),
):
    """
    Switch the active role of the currently logged-in user.
    """
    # Check if user has that role
    user_role = db.query(UserRole).filter_by(
        user_id=current_user.id,
        role=payload.new_role
    ).first()

    if not user_role:
        raise HTTPException(
            status_code=403,
            detail=f"User does not have role '{payload.new_role.value}'."
        )

    new_token = create_access_token(current_user.id, payload.new_role)

    return {
        "message": f"Switched to role '{payload.new_role.value}'.",
        "access_token": new_token,
        "token_type": "bearer"
    }


@router.post("", response_model=UserRoleResponse)
def add_role_to_user(
    role: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_without_role),
):
    if role.role != UserRoleEnum.ATTENDANT:
        raise HTTPException(status_code=400, detail="Not allowed to create this role, please create the profile.")
    return user_roles_crud.create_user_role(db, role, current_user.id)


@router.get("", response_model=List[UserRoleResponse])
def list_user_roles(db: Session = Depends(get_db), current_user = Depends(get_current_user_without_role)):
    return user_roles_crud.get_roles_for_user(db, current_user.id)


@router.delete("/{role_id}")
def remove_role(role_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Deleting a role requires ownership or admin — here we check ownership via role lookup
    db_role = user_roles_crud.get_user_role(db, role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    if db_role.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to remove this role")
    user_roles_crud.delete_user_role(db, role_id)
    return {"message": "Role removed"}
