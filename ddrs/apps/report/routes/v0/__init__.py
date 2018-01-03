from apps.report.handlers.v0 import main


routes = [

    (r'^/report$',
        main.ReportHandler),
]
