import multiprocessing

bind = "0.0.0.0:8080" # the network interface and port on which Gunicorn should bind and listen for incoming connections
workers = (multiprocessing.cpu_count() * 2) + 1 # the number of worker processes that Gunicorn should spawn to handle incoming requests concurrently
threads = 2 # the number of threads per worker process