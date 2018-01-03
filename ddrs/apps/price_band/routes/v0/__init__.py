from apps.price_band.handlers.v0 import main


routes = [

    (r'^/list$',
        main.PriceBandHandler),
    (r'^/category$',
        main.CategoryHandler),
]
