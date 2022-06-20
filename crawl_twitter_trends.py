import bs4
from twitter_crawling_bot import TwitterCrawlingBot
from config.database import init_sess


if __name__ == '__main__':
    locations = [
        #Oceania
        "Sydney, New South Wales",
        #Asia
        "Central Region, Singapore",
        "Tokyo-to, Japan",
        "Seoul, Republic of Korea",
        "Taipei City, Taiwan",
        "Hong Kong SAR China",
        "Beijing, People's Republic of China",
        "Shanghai, People's Republic of China",
        #India
        "New Delhi, India",
        #Russia
        "Moscow, Russia",
        #Europe
        "Berlin, Germany",
        "Amsterdam, The Netherlands",
        "Brussels, Belgium",
        "London, England",
        "Paris, France",
        "Madrid, Spain",
        #North America
        "New York, USA",
        "California, USA",        
        "Toronto, Ontario",
        #South America
        "Sao Paulo, Brazil"
    ]
    sess = init_sess()
    bot = TwitterCrawlingBot(headless=False)
    if bot.login():
        for location in locations:
            bot.set_trends(location=location, personalization=False)
            trends = bot.crawl_trends()
            #print(trends)
            for trend in trends:
                ts = trend.ts
                raw = trend.get_source()
                stmt = r'INSERT INTO trends (ts, location, html) VALUES (%s, %s, %s)'
                sess.cursor_insert.execute(stmt, (ts, location, raw))
                sess.cnx.commit()
            print(location, '- done')
