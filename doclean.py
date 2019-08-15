from stuff_cleaner import cleaner

base_path = 'C:\\Users\\lutz.kuenneke\\Documents'

cl = cleaner.CrawlerMaster(base_path)

cl.crawl_root()