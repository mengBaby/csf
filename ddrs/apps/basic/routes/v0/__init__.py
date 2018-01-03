from apps.basic.handlers.v0 import main


routes = [

    (r'^/store$',
     main.StoreHandler),
    (r'^/menu$',
     main.MenuHandler),
]
