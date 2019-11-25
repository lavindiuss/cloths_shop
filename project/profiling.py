import os
import psutil
import sys
from datetime import datetime, timedelta

class MemoryUsageMiddleware(object):

    def process_request(self, request):
        request._mem = psutil.Process(os.getpid()).memory_info()

    def process_response(self, request, response):
        mem = psutil.Process(os.getpid()).memory_info()
        diff = mem.rss - request._mem.rss
        with open("/var/www/html/profiling/experiment1.txt", "a") as myfile:
            now = datetime.now()+timedelta(hours=2)
            date = now.strftime("%d/%m/%Y")
            time = now.strftime("%I:%M:%S %p")
            myfile.write("%s\t%s\t%s\t%s\t%s\n" % (request.META['HTTP_HOST'], request.path, diff, date, time))
        return response