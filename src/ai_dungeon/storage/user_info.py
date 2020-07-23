from dataclasses import dataclass
from typing import Optional


@dataclass
class UserInfo:
    """
    Information about user and some state info.
    """
    token: str = None
    language: str = None

    name: str = None
    adventure: str = None
    prompt: str = None
    options: list = None


async def store_user_info(ctx, user_info: UserInfo):
    """
    Stores user info as jsonpickle to the app storage
    :param ctx: Request context
    :param user_info: Information about user
    """
    await ctx.app.storage.save(f"user:{ctx.user_uid}"
                               f"#service:{ctx.backend.get_identity()}"
                               f"#info", user_info)


async def get_user_info(ctx) -> UserInfo:
    """
    Get user info from app storage
    :param ctx: Request context
    :return: UserInfo
    """
    return await ctx.app.storage.load(f"user:{ctx.user_uid}"
                                      f"#service:{ctx.backend.get_identity()}"
                                      f"#info")


async def insert_action(ctx, adventure, action) -> bool:
    """
    Saves action if wasn't saved previously
    :param ctx: Request Context
    :param adventure: Id in format "adventure:<id>"
    :param action: Text of the action
    :return: True if new object was created, else False
    """
    action_url = f"user:{ctx.user_uid}" \
                 f"#service:{ctx.backend.get_identity()}" \
                 f"#adventure:{adventure['id']}" \
                 f"#action:{action['id']}"
    if await ctx.app.storage.load(action_url) is None:
        await ctx.app.storage.save(action_url, action['text'])
        return True
    return False
