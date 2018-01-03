from apps.overview.handlers.v0 import main


routes = [

    (r'^/list$',
        main.OverviewHandler),
    (r'^/category$',
        main.CategoryHandler),
    (r'^/list/bottom$',
        main.OverViewBottomHandler),
    (r'^/area$',
        main.AreaHandler),
]
