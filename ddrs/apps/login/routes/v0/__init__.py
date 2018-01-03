from apps.login.handlers.v0 import main


routes = [

    (r'^/login$',
        main.LoginHandler),
    (r'^/logout$',
        main.LogoutHandler),
    (r'^/identity',
        main.UserIdentityHandler),
]
