from apps.listen.handlers.v0 import main


routes = [

    (r'^/queue$',
        main.ListenQueueHandler),

]
