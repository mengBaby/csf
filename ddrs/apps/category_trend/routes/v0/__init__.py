from apps.category_trend.handlers.v0 import main


routes = [

    (r'^/month-sales$',
     main.MonthSalesHandler),
    (r'^/thirteen-weeks-sales$',
     main.ThirteenWeeksSalesHandler),
]
