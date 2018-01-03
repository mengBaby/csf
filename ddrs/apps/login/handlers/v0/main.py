from uvtor.core.decorators.api import standard_api
from apps.login.handlers import BaseHandler
from uvtor.db.models.user import User
from uvtor.db.models import manager
from models import model


class LoginHandler(BaseHandler):

    @standard_api
    async def post(self):
        secure_token = self.get_secure_cookie('_secure')
        account = self.get_argument('account')
        password = self.get_argument('password')
        secure = await User.login(account, password, secure_token)
        self.set_secure_cookie("_secure", secure)
        self.set_cookie('_xsrf', self.xsrf_token)


class LogoutHandler(BaseHandler):

    @standard_api
    async def get(self):
        secure_token = self.get_secure_cookie('_secure')
        await User.logout(secure_token)


class UserIdentityHandler(BaseHandler):

    @standard_api
    async def get(self):
        user = await self.get_current_user()
        if user.is_superuser:
            identity = 'superuser'
        else:
            chain_user = await manager.get(model.ChainUser.select().where(
                model.ChainUser.user == user
            ))
            if chain_user.is_admin:
                identity = 'manager'
            else:
                identity = 'user'
        self.set_cookie("identity", identity)
