from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status

from authentication_service.application.authentication_service import (
    AuthenticationApplicationService,
)
from authentication_service.application.dto import (
    CredentialCreateRequest,
    LoginRequest,
    PasswordChangeRequest,
    SessionResponse,
)
from authentication_service.domain.exceptions import (
    AuthenticationBlocked,
    AuthenticationDomainError,
    CredentialNotFound,
    InvalidPassword,
    SessionNotFound,
)
from authentication_service.domain.value_objects import SessionId, SessionMetadata
from authentication_service.presentation.api.runtime import get_authentication_service

router = APIRouter(prefix="/authentication", tags=["authentication"])


def trusted_tenant(request: Request, header_tenant: str | None) -> str:
    context = getattr(request.state, "tenant_context", None)
    tenant_id = getattr(context, "tenant_id", None)
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise HTTPException(status_code=403, detail="A trusted tenant context is required.1")
    if header_tenant is not None and header_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant scope does not match trusted context.")
    return tenant_id


def domain_error(exc: AuthenticationDomainError) -> HTTPException:
    if isinstance(exc, (CredentialNotFound, AuthenticationBlocked)):
        return HTTPException(status_code=401, detail="Invalid credentials.")
    if isinstance(exc, InvalidPassword):
        return HTTPException(status_code=422, detail=str(exc))
    if isinstance(exc, SessionNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


@router.post("/credentials", status_code=status.HTTP_201_CREATED)
async def create_credential(
    request_context: Request,
    body: CredentialCreateRequest,
    service: AuthenticationApplicationService = Depends(get_authentication_service),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> dict[str, str]:
    try:
        tenant = trusted_tenant(request_context, tenant_id)
        credential = await service.create_credential(
            tenant, body.user_id, body.email, body.password
        )
        return {"credential_id": str(credential.credential_id), "user_id": credential.user_id}
    except AuthenticationDomainError as exc:
        raise domain_error(exc) from exc


@router.post("/login", response_model=SessionResponse)
async def login(
    request_context: Request,
    body: LoginRequest,
    service: AuthenticationApplicationService = Depends(get_authentication_service),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> SessionResponse:
    try:
        tenant = trusted_tenant(request_context, tenant_id)
        result = await service.authenticate(
            tenant, body.email,
            body.password,
            metadata=SessionMetadata(body.user_agent, body.ip_address),
            ip_address=body.ip_address,
        )
        return SessionResponse(
            session_id=result.session_id,
            user_id=result.user_id,
            expires_at=result.expires_at,
        )
    except AuthenticationDomainError as exc:
        raise domain_error(exc) from exc


@router.post("/sessions/{session_id}/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request_context: Request,
    session_id: str,
    service: AuthenticationApplicationService = Depends(get_authentication_service),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> Response:
    try:
        await service.terminate_session(
            trusted_tenant(request_context, tenant_id), SessionId(session_id)
        )
    except AuthenticationDomainError as exc:
        raise domain_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    request_context: Request,
    session_id: str,
    service: AuthenticationApplicationService = Depends(get_authentication_service),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> SessionResponse:
    try:
        session = await service.get_session(
            trusted_tenant(request_context, tenant_id), SessionId(session_id)
        )
        return SessionResponse(
            session_id=str(session.session_id), user_id=session.user_id,
            expires_at=session.expires_at.isoformat(),
        )
    except AuthenticationDomainError as exc:
        raise domain_error(exc) from exc


@router.post("/credentials/{credential_id}/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request_context: Request,
    credential_id: str,
    body: PasswordChangeRequest,
    service: AuthenticationApplicationService = Depends(get_authentication_service),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> Response:
    try:
        await service.change_password(
            trusted_tenant(request_context, tenant_id), credential_id, body.password
        )
    except AuthenticationDomainError as exc:
        raise domain_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
