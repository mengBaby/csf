from apps.sales_trend.handlers.v0 import main


routes = [

    (r'^/year-on-year-sales$',
        main.YearSalesHandler),
    (r'^/thirteen-weeks-sales$',
        main.ThirteenWeeksSalesHandler),

]
