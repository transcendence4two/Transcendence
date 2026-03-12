from uuid import uuid4

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.settings import Settings
from src.domain.exceptions import OAuthError
from src.domain.models.user import User
from src.domain.services.commands.base import Command
from src.domain.services.token import TokenService

logger = structlog.get_logger()

GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_API_URL = "https://api.github.com"


class GithubOAuthCommand(Command):
    """Command to authenticate or register a user via GitHub OAuth."""

    def __init__(
        self,
        session: AsyncSession,
        token_service: TokenService,
        settings: Settings,
        code: str,
    ):
        self.session = session
        self.token_service = token_service
        self.settings = settings
        self.code = code

    async def execute(self) -> dict:
        access_token = await self._exchange_code_for_token()
        github_user = await self._get_github_user(access_token)
        user = await self._find_or_create_user(github_user)
        jwt = self.token_service.create_token(user.id)
        logger.info("GitHub OAuth login successful", user_id=user.id)
        return {"token": jwt, "user": user}

    async def _exchange_code_for_token(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GITHUB_TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.settings.GITHUB_CLIENT_ID,
                    "client_secret": self.settings.GITHUB_CLIENT_SECRET,
                    "code": self.code,
                    "redirect_uri": self.settings.GITHUB_OAUTH_REDIRECT_URI,
                },
                timeout=10.0,
            )
        data = response.json()
        if "error" in data:
            logger.warning("GitHub token exchange failed", error=data.get("error"))
            raise OAuthError(
                data.get("error_description", "GitHub token exchange failed")
            )
        return data["access_token"]

    async def _get_github_user(self, access_token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            user_res = await client.get(
                f"{GITHUB_API_URL}/user", headers=headers, timeout=10.0
            )
            user_data = user_res.json()

            if not user_data.get("email"):
                emails_res = await client.get(
                    f"{GITHUB_API_URL}/user/emails", headers=headers, timeout=10.0
                )
                emails = emails_res.json()
                primary = next(
                    (
                        e["email"]
                        for e in emails
                        if e.get("primary") and e.get("verified")
                    ),
                    None,
                )
                user_data["email"] = primary

        return user_data

    async def _find_or_create_user(self, github_user: dict) -> User:
        github_id = str(github_user["id"])
        email = github_user.get("email")
        github_login = github_user.get("login", "")

        # Check by oauth_id first (returning GitHub user)
        stmt = select(User).where(
            User.oauth_provider == "github", User.oauth_id == github_id
        )
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        if user:
            return user

        # Link to existing account with same email
        if email:
            stmt = select(User).where(User.email == email)
            result = await self.session.execute(stmt)
            user = result.scalars().first()
            if user:
                user.oauth_provider = "github"
                user.oauth_id = github_id
                await self.session.commit()
                await self.session.refresh(user)
                logger.info("GitHub account linked to existing user", user_id=user.id)
                return user

        if not email:
            raise OAuthError(
                "GitHub account has no verified public email. "
                "Please set a primary email on GitHub and try again."
            )

        username = await self._generate_unique_username(github_login)
        user = User(
            id=str(uuid4()),
            username=username,
            email=email,
            hashed_password=None,
            oauth_provider="github",
            oauth_id=github_id,
            enable_2fa=False,
        )
        return await self._persist(user)

    async def _generate_unique_username(self, base: str) -> str:
        stmt = select(User).where(User.username == base)
        result = await self.session.execute(stmt)
        if not result.scalars().first():
            return base

        for i in range(1, 10):
            candidate = f"{base}{i}"
            stmt = select(User).where(User.username == candidate)
            result = await self.session.execute(stmt)
            if not result.scalars().first():
                return candidate

        return f"{base}_{uuid4().hex[:6]}"
