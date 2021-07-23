import bs4
from bs4 import BeautifulSoup as soup
import requests, webbrowser, movie, sys
from movie import Movie


class Movies:
    movieName = ""

    def __init__(self, name):
        self.movieName = name.lower()

    def find_movies(self):
        print("This operation will take a few moments, we are fetching your movie data...")
        # create a name for a new file
        fileName = self.movieName + ".txt"
        f = open(fileName, "w")
        movieLinks = get_movie_links(self.movieName)
        for movie_element in movieLinks:

            # check if movie title is in the result
            # if not we move to the next movie in movieLinks
            if self.movieName not in movie_element.text.lower():
                continue

            # get the page of a specific movie, in order to extract its information
            moviePageRespond = requests.get("https://www.imdb.com" + movie_element["href"])
            moviePageSoup = soup(moviePageRespond.text.encode('utf8').decode('ascii', 'ignore'), "html.parser")
            # check if movie categorized in development mode
            if is_in_development(moviePageSoup):
                continue

            # Create movie object
            the_movie = Movie(movie_element.text)
            the_movie.mpaa_rating, the_movie.duration = get_movie_rating_and_duration(moviePageSoup)
            the_movie.genre, the_movie.directors, the_movie.stars = get_movie_genre_directors_and_stars(moviePageSoup)
            the_movie.print_to_file(f)

        f.close()


def get_movie_links(name):
    # getting the response from the Url that we need
    res = requests.get("https://www.imdb.com/find?q=" + name + "&s=tt&ttype=ft&ref_=fn_ft")
    page_soup = soup(res.text.encode('utf8').decode('ascii', 'ignore'), "html.parser")

    # get all the a tags in the result_text class, which contains the links for the specific movie page
    return page_soup.select(".result_text a")


def is_in_development(moviePageSoup):
    # getting the first div which match the class name
    movie_data = moviePageSoup.find("div", {"class": "SubNav__SubNavContentBlock-sc-11106ua-2 bAolrB"})
    # if a link is exists, the movie is in development mode and we can skip to the next movie in movieLinks
    if movie_data and movie_data.a:
        return "development" in movie_data.a.text.lower()
    return False


def get_movie_rating_and_duration(moviePageSoup):
    # find the div which contains info about: title,rating and duration of movie

    movie_data = moviePageSoup.find_all("div", {"class": "TitleBlock__TitleContainer-sc-1nlhx7j-1 jxsVNt"})
    title_block_container = movie_data[0]
    rating_and_duration_info = title_block_container.select(".ipc-inline-list__item")

    mpaa_rating = []
    duration = ""
    # check if rating and duration exists
    if len(rating_and_duration_info) < 2:
        mpaa_rating = ""
    elif len(rating_and_duration_info) == 2:
        if rating_and_duration_info[1].span:
            mpaa_rating.append(rating_and_duration_info[1].span.text.strip())
        else:
            duration = rating_and_duration_info[1].text.strip()
    else:
        mpaa_rating.append(rating_and_duration_info[1].span.text.strip())
        duration = rating_and_duration_info[2].text.strip()
    return mpaa_rating, duration


def get_movie_genre_directors_and_stars(moviePageSoup):
    # find the div which contains info about: genre,directors and stars
    movieData = moviePageSoup.find_all('div', {'class': 'Hero__MetaContainer__Video-kvkd64-4'})
    # missing movie info
    if len(movieData) == 0:
        movieData = moviePageSoup.find_all('div', {'class': 'Hero__MetaContainer__NoVideo-kvkd64-8 TqBgz'})
    genre = get_genre(moviePageSoup)
    # create a container to get the movie data
    container = movieData[0]
    directors, stars = get_directors_and_stars(container)
    return genre, directors, stars


def get_genre(moviePageSoup):
    # get the element which hold the genre info
    genre_container = moviePageSoup.find_all("a", {
        "class": "GenresAndPlot__GenreChip-cum89p-3 fzmeux ipc-chip ipc-chip--on-baseAlt"})
    genre = []
    for gen in genre_container:
        genre.append(gen.span.text.strip())
    return genre


def get_directors_and_stars(container):
    # get the div which hold the directors and stars info
    directors_and_stars_div = container.find("ul", {
        "class": "ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt"})

    directors = []
    stars = []
    # check if the directors and stars exists, if not, it will return an empty string
    if not directors_and_stars_div:
        directors = ""
        stars = ""
    else:
        directors_and_stars_container = directors_and_stars_div.select(".ipc-metadata-list__item")
        for i in directors_and_stars_container:
            span_container = i.select(".ipc-metadata-list-item__label")
            if span_container:
                for sp in span_container:
                    if sp.text.strip().lower() == "director" or sp.text.strip().lower() == "directors":
                        directors_container = i.select(".ipc-inline-list__item")
                        for j in directors_container:
                            directors.append(j.a.text)
                    if sp.text.strip().lower() == "star" or sp.text.strip().lower() == "stars":
                        stars_container = i.select(".ipc-inline-list__item")
                        for j in stars_container:
                            stars.append(j.a.text)
            else:
                if i.a.text.strip().lower() == "star" or i.a.text.strip().lower() == "stars":
                    stars_container = i.select(".ipc-inline-list__item")
                    for j in stars_container:
                        stars.append(j.a.text)
    return directors, stars

def main():
    #get the arguments from the cmd, ["movies.py","russia"]
    sys.argv
    #check if any arguments were passed to the cmd
    if len(sys.argv) > 1:
        movieName = " ".join(sys.argv[1:])
        m = Movies(movieName)
        m.find_movies()
    else:
        #no argument were passed, so open the imdb website
        webbrowser.open("https://www.imdb.com/")
        
if __name__ == '__main__':
    main()
