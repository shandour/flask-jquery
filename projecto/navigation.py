from flask_navigation import Navigation


nav = Navigation()

nav.Bar('top', [
    nav.Item('Home', 'frontend.index'),
    nav.Item('Authors', 'frontend.authors'),
    nav.Item('Books', 'frontend.books'),
    nav.Item('Useful links', 'frontend.links'),
    nav.Item('About', 'frontend.about')
])
