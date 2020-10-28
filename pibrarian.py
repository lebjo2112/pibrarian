from imdb import IMDb, IMDbError
import sqlite3, os, sys
import pib_imdb
import pib_sql as psql
import catalog
import json
import time
import wikipedia

def quit_gracefully(): #quit the program
    print("{!} Quit signal received...")
    time.sleep(1)
    conn.commit()
    conn.close()
    print("{!} SQL database saved... \nGoodbye.")
    time.sleep(1)
    sys.exit(0)

def create_media_tables(): #create inital sql tables by category
    c.execute('CREATE TABLE IF NOT EXISTS movies\
     (name TEXT, year TEXT, filepath TEXT, datapath TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS tv_shows\
     (name TEXT, year TEXT, filepath TEXT, datapath TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS music\
     (name TEXT, filepath TEXT, datapath TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS authors\
     (name TEXT,  filepath TEXT, datapath TEXT)')
    conn.commit()

def build_movie_tv_lib():
    '''cycle through uncategorized_files table,
    collect movie and tv titles into category specific tables and sets file
    paths'''
    data = get_table_data('uncategorized_files')
    showlist = []
    for row in data:
        if str(row[2]) == 'Movies':
            mdata = get_table_data('movies')
            fpath = str(row[4])
            fname = str(row[0])
            if '(' in fname:
                if './' not in fname:
                    if '._' not in fname:
                        if fname not in mdata:
                            try:
                                ty = str(fname.split(")")[0])
                                title = str(ty.split('(')[0]).strip(' ')
                                y = str(ty.split('(')[1])
                                y = str(y.split(')')[0])
                                type = 'movie'
                                t = title.split(' ')
                                tt = '_'.join(t).lower()
                                dpath = 'data/movies/' + tt + '-' + y + '.json'
                                # open(dpath, 'a+').close()
                                c.execute('INSERT INTO movies (\
                                name, year, filepath, datapath)\
                                 VALUES(?,?,?,?)', (title, y, fpath, dpath))
                                conn.commit()
                            except IndexError as e:
                                print(str(e))
                                print('\n\n')
                                print(str(l))

        if str(row[2]) == 'TV_Shows': #append tv shows to show list
            fpath = str(row[4])
            fname = str(row[3])
            tvdata = get_table_data('tv_shows')
            if '(' in fname:
                    if fname not in showlist:
                        showlist.append(str(fname))


    for fname in showlist:
        try:
            ty = str(fname.split(")")[0])
            title = str(ty.split('(')[0]).strip(' ')
            y = str(ty.split('(')[1])
            y = str(y.split(')')[0])
            type = 'tv'
            t = title.split(' ')
            tt = str('_'.join(t).lower())
            dpath = 'data/tv/' + tt + '-' + y + '.json'
            # open(dpath, 'a+').close()
            c.execute('INSERT INTO tv_shows (\
            name, year, filepath, datapath)\
             VALUES(?,?,?,?)', (title, y, fpath, dpath))
            conn.commit()
        except IndexError as e:
            print('\n\n')
            print(str(e))
            print(str(l))
    showlist = []

def collect_wiki(query, path, file):
    #dump wikipedia summary and full page to json
    try:
        summary = wikipedia.summary(query)
        page = wikipedia.WikipediaPage(query)
        data = {'summary': summary, 'page': page}
        if os.path.isfile(path + file):
            pass
        else:
            with open(path + file, 'a+') as f:
                json.dump(data, f)

    except Exception:
        print("{!} Information not found for " + str(query))
        e = open('info/errors.txt', 'a+')
        e.write(str(query) + '\n')
        e.close()
        pass

def scrape_media_info():
    '''scans sqlite database for Movies and Tv shows and collects imdb info
    into json file denoted by build_movie_tv_lib()'''

    conn = sqlite3.connect('archives.db')
    c = conn.cursor()
    pib_imdb.tvdat2json()
    pib_imdb.moviedat2json()
    conn.commit()
    menu()

def build_json_dirs():
    # make directories to store json data in
    try:
        os.mkdir('data')
        os.mkdir('data/movies/')
        os.mkdir('data/tv/')
        os.mkdir('data/actors/')
        os.mkdir('data/authors/')
        os.mkdir('data/music/')
    except FileExistsError as e:
        print(e)
        pass

def build_database(): # full program run
    build_json_dirs()
    try:
        #create tables
        catalog.create_initial_table()
        # create tables based on selected media drives
        catalog.build_categories(catalog.find_categories(catalog.set_path()))
        catalog.find_all_files() # scan directories and save results to sql DB
        conn.commit() #save
        create_media_tables()
        build_movie_tv_lib()
        conn.commit()
        pib_imdb.tvdat2json() #scan imdb for tv info
        pib_imdb.moviedat2json()# for movie info
        conn.commit()
        pib_imdb.full_casting()
        conn.commit()
    except KeyboardInterrupt:
        print("\nCTRL + C detected")
        quit_gracefully()

def scan_for_new():
    catalog.find_all_files()
    build_json_dirs()
    create_media_tables()
    build_movie_tv_lib()
    menu()
    
def menu():
    menu_options = ['Build new database', 'Build media tables',\
                    'Scrape media info', 'Actor info scrape', 'Search Database']
    x = 0

    for m in menu_options:
        x += 1
        print(str(x), ".)", str(m))
    print("[q] Quit Program")

    option = int(input(">>"))

    if option == 'q':
        quit_gracefully()
    if option == 1:
        '''Build New Database - build fresh database. make sure archives.db and
        data directory are deleted before running'''
        build_database()
        menu()
    if option == 2:
        #build media tables
        build_json_dirs()
        create_media_tables()
        build_movie_tv_lib()
        menu()
    if option == 3:
        #scrape media info from imdb
        build_json_dirs()
        try:
            scrape_media_info()
        except sqlite3.OperationalError as e:
            print(e)
            yn = str(input("Would you like to build media tables now?[y/n]: "))
            if yn == 'y':
                create_media_tables()
                build_movie_tv_lib()
                menu()
            if yn == 'n':
                menu()
    if option == 4:
        pib_imdb.full_casting()
        menu()
    if option == 5:
        kwd = input('Enter keyword: ')
        catalog.search(kwd)

def main():
    try:
        conn = sqlite3.connect('archives.db')
        c = conn.cursor()
        menu()
    except KeyboardInterrupt:
        quit_gracefully()
main()
