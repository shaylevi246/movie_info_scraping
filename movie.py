class Movie:
    name = ""
    genre = []
    mpaa_rating = []
    duration = ""
    directors = []
    stars = []

    def __init__(self, name):
        self.name = name

    def print_to_file(self, movies_file):
        # if some fields have more than one element, separate them with comma
        genre = ",".join(self.genre)
        directors = ",".join(self.directors)
        rating = ",".join(self.mpaa_rating)
        stars = ",".join(self.stars)
        # add info to file
        movies_file.write(
            self.name + "|" + genre + "|" + rating + "|" + self.duration + "|" + directors + "|" + stars + "\n")
