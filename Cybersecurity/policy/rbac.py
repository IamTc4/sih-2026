"""
Role-Based Access Control Enforcer
"""

from functools import wraps
from typing import Any, Callable
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models import (
    UserRole,
    DataClassification,
    DataPolicy,
    DEFAULT_DATA_POLICIES,
    ROLE_FIELD_ACCESS,
    ROLE_HIERARCHY,
)


class UserContext:
    """Authenticated user context with role."""

    def __init__(self, user_id: str, role: UserRole, permissions: set[str] | None = None):
        self.user_id = user_id
        self.role = role
        self.permissions = permissions or set()

    def can_access(self, classification: DataClassification) -> bool:
        """Check if user can access data of given classification."""
        allowed = ROLE_FIELD_ACCESS.get(self.role, set())
        return classification in allowed

    def can_write(self, classification: DataClassification) -> bool:
        """Check if user can write data of given classification."""
        # Only investigators, admins, and system can write confidential/restricted
        write_roles = {UserRole.INVESTIGATOR, UserRole.ADMIN, UserRole.SYSTEM}
        if classification in {DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED}:
            return self.role in write_roles
        # Analysts and above can write internal
        if classification == DataClassification.INTERNAL:
            return self.role in {UserRole.ANALYST, UserRole.INVESTIGATOR, UserRole.ADMIN, UserRole.SYSTEM}
        # All authenticated users can write public
        return self.role != UserRole.VIEWER


class RBACEnforcer:
    """
    Enforces role-based access control on API responses and data operations.
    """

    def __init__(self, policies: dict[str, DataPolicy] | None = None):
        self.policies = policies or DEFAULT_DATA_POLICIES

    def filter_response(self, data: dict[str, Any], user: UserContext) -> dict[str, Any]:
        """
        Filter response data based on user's role.
        Removes fields the user is not authorized to see.
        """
        if not isinstance(data, dict):
            return data

        filtered = {}
        for key, value in data.items():
            policy = self.policies.get(key)
            if policy is None:
                # Unknown fields default to INTERNAL (conservative)
                classification = DataClassification.INTERNAL
            else:
                classification = policy.classification

            if user.can_access(classification):
                filtered[key] = value
            else:
                # Replace with redacted indicator
                filtered[key] = f"[REDACTED: {classification.value}]"

        return filtered

    def filter_list_response(
        self,
        items: list[dict[str, Any]],
        user: UserContext
    ) -> list[dict[str, Any]]:
        """Filter a list of response objects."""
        return [self.filter_response(item, user) for item in items]

    def validate_write_access(self, data: dict[str, Any], user: UserContext) -> None:
        """
        Validate user has write access for all fields in the request.
        Raises HTTPException if not authorized.
        """
        for key in data.keys():
            policy = self.policies.get(key)
            if policy is None:
                classification = DataClassification.INTERNAL
            else:
                classification = policy.classification

            if not user.can_write(classification):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions to write field '{key}' "
                           f"(requires {classification.value} write access)"
                )

    def get_field_classification(self, field_name: str) -> DataClassification:
        """Get classification for a field."""
        policy = self.policies.get(field_name)
        return policy.classification if policy else DataClassification.INTERNAL

    def audit_access(self, user: UserContext, field_name: str, action: str) -> None:
        """Log access for audit trail (integrate with evidence trail service)."""
        policy = self.policies.get(field_name)
        if policy and policy.audit_access:
            # In production, log to evidence trail service
            pass


# Global enforcer instance
_enforcer: RBACEnforcer | None = None


def get_rbac_enforcer() -> RBACEnforcer:
    global _enforcer
    if _enforcer is None:
        _enforcer = RBACEnforcer()
    return _enforcer


# FastAPI dependency for user context
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserContext:
    """
    Extract user context from authentication token.
    In production, decode JWT and extract role/permissions.
    """
    if credentials is None:
        # Default to viewer for unauthenticated requests
        return UserContext(user_id="anonymous", role=UserRole.VIEWER)

    # TODO: Implement proper JWT validation
    # For now, simulate role extraction from token
    token = credentials.credentials

    # Simple token format: "role:user_id" (for demo only)
    if ":" in token:
        role_str, user_id = token.split(":", 1)
        try:
            role = UserRole(role_str)
        except ValueError:
            role = UserRole.VIEWER
    else:
        role = UserRole.VIEWER
        user_id = token

    return UserContext(user_id=user_id, role=role)


def require_role(*allowed_roles: UserRole):
    """Dependency to require specific role(s)."""
    def role_checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {[r.value for r in allowed_roles]}, "
                       f"got: {user.role.value}"
            )
        return user
    return role_checker


def require_classification_access(classification: DataClassification):
    """Dependency to require access to a classification level."""
    def access_checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        if not user.can_access(classification):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient clearance for {classification.value} data"
            )
        return user
    return access_checker


# Decorator for automatic response filtering
def filter_response(enforcer: RBACEnforcer | None = None):
    """Decorator to automatically filter API response based on user role."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (injected by FastAPI)
            user = kwargs.get("current_user") or kwargs.get("user")
            if user is None:
                for arg in args:
                    if isinstance(arg, UserContext):
                        user = arg
                        break

            result = await func(*args, **kwargs)

            if user and isinstance(result, dict):
                rbac = enforcer or get_rbac_enforcer()
                return rbac.filter_response(result, user)
            elif user and isinstance(result, list):
                rbac = enforcer or get_rbac_enforcer()
                return rbac.filter_list_response(result, user)

            return result
        return wrapper
    return decorator