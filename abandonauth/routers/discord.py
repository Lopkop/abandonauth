import httpx
from fastapi import APIRouter
from prisma.models import User

from abandonauth.dependencies.auth.jwt import generate_short_lived_jwt
from abandonauth.models import DiscordLoginDto, JwtDto
from abandonauth.settings import settings

router = APIRouter(
    prefix="/discord",
    tags=["Discord"],
)

DISCORD_API_BASE = "https://discord.com/api/v10"


async def login_with_discord(login_data: DiscordLoginDto, application_id: str) -> JwtDto:
    """Log a user in using Discord's OAuth2 as validation."""
    # Gather access token
    data = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "client_secret": settings.DISCORD_CLIENT_SECRET.get_secret_value(),
        "grant_type": "authorization_code",
        "code": login_data.code,
        "redirect_uri": login_data.redirect_uri,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post(f"{DISCORD_API_BASE}/oauth2/token", data=data)
        response.raise_for_status()

        token = response.json()["access_token"]

        response = await client.get(
            f"{DISCORD_API_BASE}/users/@me",
            headers={"Authorization": f"Bearer {token}"},
        )

        response.raise_for_status()
        discord_user = response.json()

    user = await User.prisma().find_first(
        where={
            "discord_account": {
                "is": {
                    "id": int(discord_user["id"]),
                },
            },
        },
    )

    if user is None:
        user = await User.prisma().create({
            "username": discord_user["username"],
            "discord_account": {
                "create": {
                    "id": int(discord_user["id"]),
                },
            },
        })

    return JwtDto(token=generate_short_lived_jwt(user.id, application_id))
