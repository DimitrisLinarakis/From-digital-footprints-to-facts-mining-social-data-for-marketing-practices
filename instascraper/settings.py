BOT_NAME = 'instascraper'
SPIDER_MODULES = ['instascraper.spiders']
NEWSPIDER_MODULE = 'instascraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
LOG_LEVEL = "INFO"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 5

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 5
DOWNLOAD_TIMEOUT = 110
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
#SPIDER_MIDDLEWARES = {
#    'instascraper.middlewares.InstascraperSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
#DOWNLOADER_MIDDLEWARES = {
    #'instascraper.middlewares.InstascraperDownloaderMiddleware': 543
#}

# Enable or disable extensions
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
ITEM_PIPELINES = {
    'instascraper.pipelines.DatabasePipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 110
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
