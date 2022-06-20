import bs4
import re
import conn_mysql
import utilities
import sys

if __name__ == '__main__':
    config = utilities.get_config('mysql')
    sess = conn_mysql.main(config)
    stmt = f'SELECT id, html FROM trends WHERE is_parsed = False'
    sess.cursor_select.execute(stmt)
    raw = sess.cursor_select.fetchone()
    while raw:
        id_ = raw.get('id')
        html = raw.get('html')
        soup = bs4.BeautifulSoup(html, 'html.parser')
        if soup:
            if soup.find('div'):
                if soup.find('div').find('div'):
                    structure = soup.find('div').find('div').find_all('div', recursive=False)
                    structure.pop()
                    
                    header = structure[0].get_text()
                    header = re.sub(r'·', ' ',header)
                    if header:
                        header = ' '.join(header.split())
                        m = re.search(r'(\d+)\s((.*)\s)?Trending', header)
                        if m:
                            index = m.group(1)
                            category = m.group(3)
                    
                    title = structure[1].get_text()

                    content = None
                    tweets = None
                    trendingwith = None
                    quote = None

                    for div in structure[2:]:
                        raw_text = div.get_text()
                        if raw_text:
                            text = ' '.join(raw_text.split())
                            if text.lower()[-6:] == 'tweets':
                                tweets_text = div.get_text()
                                tweets_text = re.sub(',', '', tweets_text)
                                m = re.search(r'(\d*\.?\d+K?M?)', tweets_text)
                                if m:
                                    tweets_text = m.group(1)
                                    if 'M' in tweets_text:
                                        n = re.search(r'(\d*\.?\d+)', tweets_text)
                                        if n:
                                            tweets = int(float(n.group(1)) * 1000000)
                                    elif 'K' in tweets_text:
                                        n = re.search(r'(\d*\.?\d+)', tweets_text)
                                        if n:
                                            tweets = int(float(n.group(1)) * 1000)
                                    else:
                                        tweets = int(tweets_text)                                
                            elif text.lower()[:13] == 'trending with':
                                trendingwith = div.get_text()
                            elif text.lower()[:11] == 'quote tweet':
                                quote = ' '.join([' '.join(_.get_text().split()) for _ in div.find_all('span') if _.get_text().split()][2:])
                            else:
                                content = div.get_text()
                    
                    stmt = f'''
                        UPDATE trends 
                        SET 
                            data_index = %s, 
                            data_category = %s, 
                            data_title = %s, 
                            data_content = %s, 
                            data_quote = %s, 
                            data_tweets = %s, 
                            data_trendingwith = %s 
                        WHERE id = %s'''
                    print(index, category, title, content, quote, tweets, trendingwith, id_)
                    sess.cursor_insert.execute(stmt, (index, category, title, content, quote, tweets, trendingwith, id_))
                    sess.cnx.commit()

        raw = sess.cursor_select.fetchone()