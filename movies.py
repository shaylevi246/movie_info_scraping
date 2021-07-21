import bs4
from bs4 import BeautifulSoup as soup
import requests, sys, webbrowser

#get the arguments from the cmd, ["movies.py","russia"]
sys.argv

#check if any arguments were passed to the cmd
if len(sys.argv) > 1:
    movieName = " ".join(sys.argv[1:])
    movieName = movieName.lower()

# create a name for a new file
    fileName = movieName + ".txt"
    f = open(fileName, "w")

    # getting the response from the Url that we need
    res = requests.get("https://www.imdb.com/find?q=" + movieName + "&s=tt&ttype=ft&ref_=fn_ft")
    page_soup = soup(res.text.encode('utf8').decode('ascii', 'ignore'), "html.parser")

    # get all the a tags in the result_text class, which contains the links for the specific movie page
    movieLinks = page_soup.select(".result_text a")
    for movie in movieLinks:

        # check if movie title is in the result
        # if not we move to the next movie in movieLinks
        if movieName not in movie.text.lower():
            continue

        # get the page of a specific movie, in order to extract its information
        moviePageRespond = requests.get("https://www.imdb.com" + movie["href"])
        moviePageSoup = soup(moviePageRespond.text.encode('utf8').decode('ascii', 'ignore'), "html.parser")

        # check if movie categorized in development mode
        # getting the first div which match the class name
        movie_data = moviePageSoup.find("div", {"class": "SubNav__SubNavContentBlock-sc-11106ua-2 bAolrB"})
        # if a link is exists, the movie is in development mode and we can skip to the next movie in movieLinks
        if movie_data and movie_data.a:
            if "development" in movie_data.a.text.lower():
                continue

        # find the div which contains info about: title,rating and duration of movie

        movie_data = moviePageSoup.find_all("div", {"class": "TitleBlock__TitleContainer-sc-1nlhx7j-1 jxsVNt"})
        title_block_container = movie_data[0]
        movie_title = title_block_container.h1.text
        movie_MPAA_rating = []
        movie_duration = ""

        rating_and_duration_info = title_block_container.select(".ipc-inline-list__item")
        # check if rating and duration exists
        if len(rating_and_duration_info) < 2:
            movie_MPAA_rating = ""
            movie_duration = ""
        elif len(rating_and_duration_info) == 2:
            if rating_and_duration_info[1].span:
                movie_MPAA_rating.append(rating_and_duration_info[1].span.text.strip())
            else:
                movie_duration = rating_and_duration_info[1].text.strip()
        else:
            movie_MPAA_rating.append(rating_and_duration_info[1].span.text.strip())
            movie_duration = rating_and_duration_info[2].text.strip()

        #
        #
        # find the div which contains info about: genre,directors and stars
        movieData = moviePageSoup.find_all('div', {'class': 'Hero__MetaContainer__Video-kvkd64-4'})
        # missing movie info
        if len(movieData) == 0:
            movieData = moviePageSoup.find_all('div', {'class': 'Hero__MetaContainer__NoVideo-kvkd64-8 TqBgz'})

        # create a container to get the movie data
        container = movieData[0]

        # get the element which hold the genre info
        genre_container = moviePageSoup.find_all("a", {
            "class": "GenresAndPlot__GenreChip-cum89p-3 fzmeux ipc-chip ipc-chip--on-baseAlt"})

        # create an array to hold all the movie genres
        movie_genre = []
        for gen in genre_container:
            movie_genre.append(gen.span.text.strip())

        movie_directors = []
        movie_stars = []
        # get the div which hold the directors and stars info
        directors_and_stars_div = container.find("ul", {
            "class": "ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt"})

        # check if the directors and stars exists, if not, it will return an empty string
        if not directors_and_stars_div:
            movie_directors = ""
            movie_stars = ""
        else:
            directors_and_stars_container = directors_and_stars_div.select(".ipc-metadata-list__item")
            for i in directors_and_stars_container:
                span_container = i.select(".ipc-metadata-list-item__label")
                if span_container:
                    for sp in span_container:
                        if sp.text.strip().lower() == "director" or sp.text.strip().lower() == "directors":
                            directors_container = i.select(".ipc-inline-list__item")
                            for j in directors_container:
                                movie_directors.append(j.a.text)
                        if sp.text.strip().lower() == "star" or sp.text.strip().lower() == "stars":
                            stars_container = i.select(".ipc-inline-list__item")
                            for j in stars_container:
                                movie_stars.append(j.a.text)
                else:
                    if i.a.text.strip().lower() == "star" or i.a.text.strip().lower() == "stars":
                        stars_container = i.select(".ipc-inline-list__item")
                        for j in stars_container:
                            movie_stars.append(j.a.text)
        # if some fields have more than one element, separate them with comma
        genre = ",".join(movie_genre)
        directors = ",".join(movie_directors)
        rating = ",".join(movie_MPAA_rating)
        stars = ",".join(movie_stars)
        # add info to file
        f.write(movie_title + "|" + genre + "|" + rating + "|" + movie_duration + "|" + directors + "|" + stars + "\n")
    f.close()
else:
    #no argument were passed, so open the imdb website
    webbrowser.open("https://www.imdb.com/")





