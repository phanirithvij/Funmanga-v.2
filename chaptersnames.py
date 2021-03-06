import sqlite3
from bs4 import BeautifulSoup as soup
from requests import request

conn = sqlite3.connect("fun_slugid.db")
c = conn.cursor()

c.execute("SELECT manga_slug FROM funmanga")
allmanga = c.fetchall()

c.close()
conn.close()

conn = sqlite3.connect("fun_chapternames.db")
c = conn.cursor()


for manga_slug in allmanga:
    c.execute("SELECT * FROM funmanga WHERE manga_slug = ?", [manga_slug[0]])

    results = c.fetchone()

    if results != [] and results != None:
        print(manga_slug[0])
    else:
        
        req = request("GET", "http://www.funmanga.com/" + manga_slug[0])

        resp = req.text

        html_soup = soup(resp, "lxml")

        ul = html_soup.find("ul", {"class":"chapter-list"})

        run = True

        try:
            lis = ul.findAll("li")
        except Exception as e:
            print(e)
            run = False
            #This happens when 404


        if run:
            for li in lis:
                chapter_link = li.a["href"]
                chapter_link = "/".join(chapter_link.split("/")[3:])
                
                c.execute("SELECT * FROM funmanga WHERE fun_chapter_link = ?", [chapter_link])
                results = c.fetchone()
                
                if results != None and results != []:
                    print(results,"results")
                else:
                    try:
                        chapter_no = chapter_link.split("/")[1]
                    except Exception as e:
                        print("cannot split by '/'")
                        #eg: http://www.funmanga.com/Biyaku-Cafe
                        #This error occured
                        print(e)
                    chapter_name = li.a.span.text.strip()

                    c.execute("INSERT INTO funmanga (chapter_name, fun_chapter_link, manga_slug, chapter_no) VALUES (?,?,?,?)", (chapter_name, chapter_link, manga_slug[0], chapter_no))
                    print("inserted", manga_slug[0], chapter_no, chapter_name, chapter_link)
        else:
            print("Skipped", manga_slug[0])
            #This happens when 404
    conn.commit()

c.close()
conn.close()