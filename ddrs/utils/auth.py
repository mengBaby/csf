from uvtor.conf import settings
import urllib.parse as urlparse
from urllib.parse import urlencode
from uvtor.core import exceptions
from uvtor.db.models import manager
from models.model import ChainUser


def login_required(func):
    async def decorator(self, *args, **kwargs):
        user = await self.get_current_user()
        if not user:
            if self.request.method in ("GET", "HEAD"):
                url = settings.LOGIN_URL
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise exceptions.LoginRequired
        else:
            result = await func(self, *args, **kwargs)
            return result

    return decorator


def sys_admin_required(func):
    async def decorator(self, *args, **kwargs):
        user = await self.get_current_user()
        if not user:
            raise exceptions.LoginRequired
        if user.is_active and user.is_superuser:
            result = await func(self, *args, **kwargs)
            return result
        else:
            raise exceptions.PermissionDenied

    return decorator


def admin_required(func):
    async def decorator(self, *args, **kwargs):
        user = await self.get_current_user()
        if not user:
            raise exceptions.LoginRequired
        if user.is_superuser:
            result = await func(self, *args, **kwargs)
            return result
        else:
            chain_user = ChainUser.get(
                user=user
            )
            if user.is_active and chain_user.is_admin:
                result = await func(self, *args, **kwargs)
                return result
            else:
                raise exceptions.PermissionDenied

    return decorator
