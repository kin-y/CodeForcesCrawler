from pyquery import PyQuery as pq
import requests as req
import time
import json
import os, os.path

base_url = 'http://codeforces.com/'
url = base_url + 'api/'
userfile = 'data/users.json'

rating = [
    2900,
    2600,
    2400,
    2300,
    2200,
    1900,
    1600,
    1400,
    1200,
    0,
]

inf = 10000000


def getData(api, option):
    time.sleep(1)
    return req.get(url+api, params=option).json()


def getUserData(option):
    if not os.path.isfile(userfile):
        users = getData('user.ratedList', {'activeOnly': 'true'})
        saveAsJson(users, userfile)
        return users
    else:
        return loadData(userfile)


def getSampleUsers(n=inf):
    users = getUserData({'activeOnly': 'true'})
    user_list = []
    count = [0]*len(rating)
    idx = 0
    for user in users['result']:
        if user['rating'] < rating[idx]:
            idx += 1
        if idx >= len(rating):
            break
        if count[idx] >= n:
            continue
        user_list.append(user['handle'])
        count[idx] += 1
    return user_list


def getUsers(datalist, n=inf):
    users = getUserData({'activeOnly': 'true'})['result']
    user_list = []
    count = 0
    for user in users:
        count += 1
        if count > n:
            break
        data = {}
        for (cf_name, db_name) in datalist.items():
            if not cf_name in user:
                print('Wrong datalist. Key %s was not found' % cf_name)
            data[db_name] = user[cf_name]
        user_list.append(data)
    return user_list


def saveAsJson(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))


def getSource(prob_id, contest_id):
    dom = pq(base_url + 'contest/%d/submission/%d' % (contest_id, prob_id))
    return dom.find('pre.prettyprint.program-source').text()


# get recent n sources
# return source list
def recentSources(username, n):
    query = {
        'handle': username,
        'count': n
    }
    submissions = getData('user.status', query)['result']
    source = []
    print("%s's source" % username)
    for status in submissions:
        print('getting source id=%d' % status['id'])
        time.sleep(1)
        prob_id = status['id']
        contest_id = status['contest_Id']
        data = {}
        data['source'] = getSource(prob_id, contest_id)
        data['prob_id'] = prob_id
        data['contest_id'] = contest_id
        data['lang'] = status['programmingLanguage']
        data['verdict'] = status['verdict']
        source.append(data)
    return source


def loadData(filename):
    data = None
    with open(filename, encoding='utf-8') as f:
        data = json.loads(f.read())
    return data


def saveFile(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def init():
    if not os.path.isdir('data'):
        os.mkdir('data')
    

filename = 'data/sample.json'
userdata_format = {
    'handle': 'user_name',
    'rating': 'rating',
    'maxRating': 'max_rating'
}
if __name__ == '__main__':
    init()
    
    user_list = getUsers(userdata_format, 10)
    db = Database()

    for user in user_list[:2]:
        db.addUser(user)
        handle = user['user_name']
        source = recentSources(handle, 2)
        for src in source:
            filename = '%s_%s_%s.src'
            saveFile(filename, src['source'])
            db.addFile(handle, filename, src['lang'], src['verdict'])

    print('UserTable: ')
    db.showUserTable()
    print('FileTable: ')
    db.showFileTable()

    db.close()
