from apps.ring_analysis.handlers.v0 import main


routes = [

    (r'^/sun-figure$',
        main.SunFigureHandler),
    (r'^/sales-diff$',
        main.SalesDiffHandler),

]
