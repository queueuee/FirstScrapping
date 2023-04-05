import requests
from mysql.connector import connect, Error
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
import time
from typing import Final

host: Final[str] = "localhost"
db_user: Final[str] = "Admin"
passwrd: Final[str] = "pepega"
db_name: Final[str] = "scrapping"
news_table: Final[str] = "securitylab_news"


def get_news(url):
    user = UserAgent().random
    header = {'user-agent': user}
    r = requests.get(url=url, headers=header)

    soup = BeautifulSoup(r.text, "lxml")

    url = url.rsplit('/', 2)[0]
    article_cards = soup.find_all("a", class_="article-card inline-card")

    try:
        with connect(
                host=host,
                user=db_user,
                password=passwrd,
                database=db_name
        ) as connection:
            create_table = "CREATE TABLE IF NOT EXISTS " + news_table + "(" \
                           "id INT AUTO_INCREMENT PRIMARY KEY," \
                           "title VARCHAR(1000)," \
                           "descrb VARCHAR(9000)," \
                           "article_url VARCHAR(100)," \
                           "article_data_timestamp DATETIME)"
            with connection.cursor() as cursor:
                cursor.execute(create_table)

            insert_news = """
                INSERT INTO """ + news_table + """
                (title, descrb, article_url, article_data_timestamp)
                VALUES ( %s, %s, %s, %s )
                """

            for article in article_cards:
                title = article.find("h2", class_="article-card-title").text.strip()
                descrb = article.find("p").text.strip()
                article_url = url + article.get("href")

                article_date_time = article.find("time").get("datetime")
                date_from_iso = datetime.fromisoformat(article_date_time)
                date_time = datetime.strftime(date_from_iso, "%Y-%m-%d %H:%M:%S")
                article_data_timestamp = time.mktime(datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timetuple())
                data_time = datetime.utcfromtimestamp(article_data_timestamp)

                new = [(title, descrb, article_url, data_time)]
                with connection.cursor() as cursor:
                    cursor.executemany(insert_news, new)
                    connection.commit()

            get_data = "SELECT * FROM " + news_table

            with connection.cursor() as cursor:
                cursor.execute(get_data)
                result = cursor.fetchall()
                for lines in result:
                    print(lines)

    except Exception as e:
        print("Bad server :(")
        print(e)


def main():
    get_news('https://www.securitylab.ru/news/')


if __name__ == '__main__':
    main()
