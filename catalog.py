# Specify drives designated for backup_storage
# recursively scans drives and stores in sql database

import os, sys, datetime
import pib_sql as psql
from getpass import getuser
import time
import pib_imdb as pmdb
def check_os():
    #discover host os
    os = sys.platform
    if os == 'linux' or os == 'linux2':
        mountedpath = '/media/' + str(getuser()) + '/'
    elif os == 'darwin':
        mountedpath = '/Volumes/'
    elif os == 'win32':
        print('Windows compatability not currently avaliable.')
    return mountedpath

def set_path():
    # scan mount points for external drives
    mountedpath = check_os()
    categories = os.listdir(mountedpath)
    x = 0
    drive_list = []
    for drive in categories:
        x += 1
        print(str(x), mountedpath + str(drive))

    no_of_drives = int(input("Enter total number of backupdrives conneced (integer): "))

    for r in range(0,no_of_drives):
        arc_drive = int(input("Enter number asssociated with drive: "))
        arc_path = mountedpath+ str(categories[arc_drive - 1])
        drive_list.append(arc_path + '/')
        print('drives added: ')
        for d in drive_list:
            print(str(d))

    return drive_list

def find_categories(drive_list):
    #find sub directories of given drive list
    cat_dic = {}
    for path in drive_list:
        path = str(path)

        os.chdir(path)
        categories = os.listdir()
        category_list = []
        selected_list = []
        for cat in categories:
            if '.' in str(cat): #ignore hidden files
                pass
            else:
                category_list.append(path + str(cat) + "/")

        print('Categories found in:', path)

        x = 0
        for c in category_list:
            x += 1
            print(str(x) + '. ' + str(c))

        cat_dic.update({path:category_list})
    print(cat_dic)
    return cat_dic

def build_categories(cat_dic):
    #takes category dictionary and creates sql db tables
    print("\nCategories")
    for key in cat_dic:
        opath = str(key)
        cat_list = cat_dic[key]
        for category in cat_list:
            if 'Volume' in category:
                pass
            else:
                title = str(category.split('/')[-2])
                path = opath + title + '/'

                psql.c.execute("INSERT INTO categories(name, fullpath)\
                 VALUES(?,?)", (title, path))
                print(path)
                path = ''

def create_initial_table():
    #create basic tables for processing
    print('creating category and uncategorized tables')
    psql.c.execute("CREATE TABLE IF NOT EXISTS categories\
     (name TEXT, fullpath TEXT)")
    psql.c.execute('CREATE TABLE IF NOT EXISTS uncategorized_files\
     (name TEXT, date_added TEXT, category TEXT, sub_cat TEXT, full_path TEXT)')

def find_all_files():
    #scan all directories for all files (with typical extensions)
    drive_list = []
    psql.c.execute('SELECT * FROM categories')
    data = psql.c.fetchall()
    for r in data:
        d = str(r[1])
        result = [os.path.join(dp, f)\
         for dp, dn, filenames in os.walk(str(d))\
          for f in filenames if '.' in str(os.path)]
        for r in result: # skip if result is already in db
            sqldata = psql.c.execute('SELECT * FROM uncategorized_files')
            if r in sqldata:
                break
            else:
                try:
                    #   chop data for writing to sql
                    date = datetime.datetime.now()
                    full_path = str(r)
                    type_split = r.split('.')[1]
                    ext = '.' + str(type_split)
                    path_split = r.split('/')
                    category = str(path_split[5])
                    sub_cat = str(path_split[6])
                    name = str(path_split[-1])
                    print('Adding file to sql-database: ' + name)
                    psql.c.execute('INSERT INTO uncategorized_files VALUES (?,?,?,?,?)',\
                    (name, str(date), category, sub_cat, full_path))
                    psql.conn.commit()
                except IndexError:
                    pass

def cat_table_create(name, value_string):
    #create category tables
    create_table = "CREATE TABLE IF NOT EXISTS "
    table_cmd = create_table + str(name) + ' ' + str(value_string)
    psql.c.execute(table_cmd)

def search(kwd):
    data = psql.get_table_data('uncategorized_files')
    print("...searching files")
    print("--Matches--\n")
    for r in data:
        if kwd.lower() in r:
            print(r)

def main():
    create_initial_table() #create tables
    build_categories(find_categories(set_path()))
    find_all_files()
    psql.conn.commit()
