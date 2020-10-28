'''
Pibrarian-IMDB Module
Collects info on tv series and movies in personal library from IMDB and
  saves information to .json files for futher processing
'''
from imdb import IMDb, IMDbError
import time
import pib_sql as psql
import sqlite3, os
import json

ia = IMDb()
movie_infoset = ['airing', 'akas', 'alternate versions', 'awards',\
 'connections','crazy credits', 'critic reviews', 'episodes',\
  'external reviews', 'external sites', 'faqs', 'full credits',\
   'goofs', 'keywords', 'list', 'locations', 'main', 'misc sites',\
    'news', 'official sites', 'parents guide', 'photo sites', 'plot',\
     'quotes', 'recommendations', 'release dates', 'release info',\
      'reviews', 'sound clips', 'soundtrack', 'synopsis', 'taglines',\
       'technical', 'trivia','tv schedule','video clips','vote details']
person_infoset = ['awards', 'biography', 'filmography',\
 'genres links', 'keywords links', 'main', 'news', 'official sites',\
 'other works', 'publicity']


def search_imdb(title, year):
    # search imdb for media title
    search = title + ' ' + year
    print('\n\n{!} Searching:', search, '\n\n')

    results = ia.search_movie(str(search))
    print('{!} Search Results:')
    try:
        movie = results[0]
        print("Title", movie)
        print("ID: ", movie.movieID)
        movie = ia.get_movie(movie.movieID)

    except IndexError as e:
        pass
    except IMDbError as e:
        print('\n', str(e),'\n\n')
        pass
    try:
        return movie
    except UnboundLocalError:
        pass

def moviedat2json():
    # scrape imdb for movie table
    ia = IMDb()
    movie_data = psql.get_table_data('movies')
    for r in movie_data:
        title = str(r[0])
        year = str(r[1])
        data_file = str(r[3])

        if os.path.isfile(data_file):
            pass

        else:
            try:
                movie = search_imdb(title, year)
                movie.infoset2keys
                mkeys = ['original title', 'cast', 'genres',\
                 'runtimes', 'original air date', 'rating', 'votes',\
                  'cover url', 'imdbID', 'plot outline', 'title', 'year',\
                   'kind', 'directors', 'writers', 'producers', 'composers',\
                    'writer', 'director', 'production companies',\
                     'plot', 'synopsis']
                data = {}
                for k in mkeys:
                    try:
                        # print('\n')
                        # print(str(k))
                        # print(str(movie[str(k)]))
                        data.update({str(k):str(movie[str(k)])})
                    except KeyError as e:
                        data.update({str(k):None})
                with open(data_file, 'a+') as f:
                    json.dump(data, f)
            except AttributeError as e:
                print(e)
                pass

def tvdat2json():
    # scrape table for tv list
    # redundant!
    ia = IMDb()
    tv_data = psql.get_table_data('tv_shows')
    for r in tv_data:
        title = str(r[0])
        year = str(r[1])
        data_file = str(r[3])
        if os.path.isfile(data_file):
            pass
        else:
            try:
                series = search_imdb(title, year)
                try:
                    series.infoset2keys
                except (AttributeError, imdb.IMDbError) as e:
                    print(e)
                    pass
                data = {}
                seasonepi = {}
                keys = ['original title', 'episodes', 'cast', 'genres',\
                 'runtimes', 'original air date', 'rating', 'votes',\
                  'cover url', 'imdbID', 'plot outline', 'title', 'year',\
                   'kind', 'directors', 'writers', 'producers', 'composers',\
                    'writer', 'director', 'production companies',\
                     'plot', 'synopsis']
                seasons = ia.update(series, 'episodes')
                season = {}
                print('seasons:')
                try:
                    print(sorted(series['episodes'].keys()))
                    for s in range(1,len(sorted(series['episodes'].keys()))+1):
                        episode_count = len(series['episodes'][s])
                        print('episodes in season:', str(s),'\n', episode_count)
                        print(seasons)
                except (KeyError, TypeError) as e:
                    pass
                try:
                    for k in keys:
                        print('\n')
                        print(str(k))
                        print(str(series[str(k)]))
                        data.update({str(k):str(series[str(k)])})
                except KeyError as e:
                    data.update({str(k):None})
                with open(data_file, 'a+') as f:
                    json.dump(data, f)

            except (IndexError) as e:
                pass
            except IMDbError as e:
                print("\n\ne\n\n")
                pass

def get_cast_info(file):
    l = ['movies', 'tv']
    ia = IMDb()
    for i in l:
        try:
            with open('data/' +str(i)+'/'+ file, 'r') as f:
                data = json.load(f)
                cast = data['cast']
                cast = cast.split(',')
                cast_dic = {}
                #process name
                for c in cast:
                    s = c.split(' ')
                    name_start = len(s) - 2
                    name_list = []
                    for i in range(name_start, len(s)):
                        name_list.append(str(s[i]))
                    n1 = ' '.join(name_list)
                    n2 = str(n1.split('_')[1])
                    if n2 == ">":
                        pass
                    else:
                        name = n2

                #process ID
                for c in cast:
                    s = c.split(' ')
                    id = str(s[2]).split(':')[1]
                    print(id)
                    try:
                        write_actor_info(id)

                    except IMDbError as e:
                        print('error')
                        pass
        except FileNotFoundError as e:
            print(e)
            pass

def write_actor_info(name, id):
    ia = IMDb()
    info = ia.get_person(id)
    data = {}
    save_path = 'data/actors/'
    for i in person_infoset:
        # print(i)
        try:
            # print(str(i))
            # print(info[str(i)])
            data.update({str(i): str(info[str(i)])})

        except KeyError:
            print("Key Error extracting:", str(i))
            print("\tin", info)
            data.update({str(i):None})
    with open(save_path + str(name) +'.json', 'a+') as f:
        json.dump(data,f)

def full_casting():
    for f in os.listdir('data/movies/'):
        get_cast_info(f)

    for f in os.listdir('data/tv/'):
        get_cast_info(f)


def temp_movie_search(title, year):
    ia = IMDb()
    data_file = 'data/temp_imdb/' + str(title) + '-' + str(year) + '.json'
    if os.path.isfile(data_file):
        pass

    else:
        try:
            movie = search_imdb(title, year)
            movie.infoset2keys
            mkeys = ['original title', 'cast', 'genres',\
             'runtimes', 'original air date', 'rating', 'votes',\
              'cover url', 'imdbID', 'plot outline', 'title', 'year',\
               'kind', 'directors', 'writers', 'producers', 'composers',\
                'writer', 'director', 'production companies',\
                 'plot', 'synopsis']
            data = {}
            for k in mkeys:
                try:
                    # print('\n')
                    # print(str(k))
                    # print(str(movie[str(k)]))
                    data.update({str(k):str(movie[str(k)])})
                except KeyError as e:
                    data.update({str(k):None})
            with open(data_file, 'a+') as f:
                json.dump(data, f)
        except (Exception) as e:
            print(e)
            pass

def temp_data_pull():
    with open('data/temp/movies.txt', 'r') as movies:
        for l in movies.readlines():
            l = str(l.strip("\n"))
            if "./" in str(l):
                pass
            else:
                try:
                    t = str(l.split('(')[0]).strip(' ')
                    y = str(l.split(')')[0].split('(')[1])
                    temp_movie_search(t,y)
                except IndexError as e:
                    print(e)
                    pass

    with open('data/temp/tv_shows.txt', 'r') as movies:
        for l in movies.readlines():
            l = str(l.strip("\n"))
            if "./" in str(l):
                pass
            else:
                try:
                    t = str(l.split('(')[0]).strip(' ')
                    y = str(l.split(')')[0].split('(')[1])
                    temp_movie_search(t,y)
                except IndexError as e:
                    print(e)
                    pass

def temp_actor_pull():
    srcpath = 'data/temp_imdb/'
    destpath = 'data/actors/'
    actor_list = []
    actor_dict = {}
    for i in os.listdir(srcpath):
        try:
            print("Extracting cast info for: " + str(i))
            with open(srcpath + str(i), 'r') as f:
                data = json.load(f)
                cast = data['cast']
                cast = cast.split(',')
                cast_dic = {}
                #process name
                for c in cast:
                    s = c.split(' ')
                    print(s)
                    name_start = len(s) - 2
                    name_list = []
                    id = str(str(str(s[1]).split(':')[1]).split("[")[0])
                    for i in range(name_start, len(s)):
                        name_list.append(str(s[i]))
                    n1 = ' '.join(name_list)
                    n2 = str(n1.split('_')[1])
                    print(n1)
                    print(n2)
                    if n2 == ">":
                        pass
                    else:
                        name = str(n2)
                        if name in actor_dict:
                            # print(name, 'has already been processed. Moving On.')
                            pass
                        else:
                            actor_dict.update({name:str(id)})


        except Exception as e:
            print(e)
            pass
    x = 0
    for k in actor_dict:
        x +=1
    print(str(x), ") Actors ready to be Scraped")
    print("...")
    time.sleep(2)
    print("Preparing to retreieve imdb page.")
    for k in actor_dict:
        name = str(k)
        id = str(actor_dict[(str(k))])
        write_actor_info(name, id)
