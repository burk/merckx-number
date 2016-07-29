import json
import numpy as np
import pickle
import sys
import tables
from collections import defaultdict


def read_data(fname):

    with open(fname) as data_file:
        data = json.load(data_file)

    return data


def print_mat(neighbors):

    f = open('initial_dist', 'w')
    n = len(neighbors)
    f.write(str(n))
    f.write("\n")

    dist = np.ones((n, n), dtype=np.int32) * 2 ** 30 / 2

    for x in neighbors.keys():
        dist[x, x] = 0
        for y in neighbors[x]:
            dist[x, y] = 1

    for i in range(n):
        for j in range(n):
            f.write(str(dist[i, j]))
            f.write(" ")

        f.write("\n")

    f.close()


def floyd_warshall(neighbors):

    n = len(neighbors)

    dist = np.ones((n, n), dtype=np.int32) * 2 ** 30 / 2
    nxtv = np.ones((n, n), dtype=np.int32) * -1

    for x in neighbors.keys():
        for y in neighbors[x]:
            dist[x, y] = 1

    print "n =", n
    for k in range(n):
        print "At k =", k
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
                    nxtv[i, j] = nxtv[i, k]

    return dist, nxtv


def main():

    data = read_data('items.json')

    riders = {}
    teams = {}

    num_to_rider = {}
    rider_to_num = {}

    team_to_num = {}

    i = 0
    ti = 0

    rider_arr = []
    team_arr = []

    for item in data:
        if 'rider' in item:
            #print u"RIDER {}".format(item[u'name'])
            riders[item[u'rider'].lower()] = item
            num_to_rider[i] = item[u'rider'].lower()
            rider_to_num[item[u'rider'].lower()] = i
            item[u'index'] = i
            rider_arr.append(item)
            i += 1

        if 'team' in item:
            #print u"TEAM {}".format(item[u'name'])
            teams[item[u'team'].lower()] = item
            team_to_num[item[u'team'].lower()] = ti
            item[u'index'] = i
            team_arr.append(item)
            ti += 1

    n = len(riders)

    neighbors = {}

    team_conn = {}
    for team in teams.keys():
        for x in teams[team][u'riders']:
            x = x.lower()
            if rider_to_num[x] not in neighbors:
                neighbors[rider_to_num[x]] = []
            for y in teams[team][u'riders']:
                y = y.lower()
                team_conn[(rider_to_num[x], rider_to_num[y])] = team_to_num[team.lower()]
                if x != y:
                    neighbors[rider_to_num[x]].append(rider_to_num[y])

    for i in range(len(team_arr)):
        del team_arr[i][u'riders']

    print team_arr[0:10]

    print "Printing matrices to file."
    print_mat(neighbors)

    print "Dumping team connections."
    pickle.dump(team_conn, open('team_conn.p', 'wb'))
    print "Dumping rider array."
    pickle.dump(rider_arr, open('rider_arr.p', 'wb'))
    print "Dumping team array."
    pickle.dump(team_arr, open('team_arr.p', 'wb'))


def conv_mats(n):

    print "Converting matrices to HDF5."

    dist = np.zeros((n, n), dtype=np.int32)
    fin = open('dist', 'r')
    i = 0
    for line in fin:
        dist[i, :] = map(int, line.split())
        i += 1

    nxtv = np.zeros((n, n), dtype=np.int32)
    fin = open('next', 'r')
    i = 0
    for line in fin:
        nxtv[i, :] = map(int, line.split())
        i += 1

    print "Dists and nexts loaded."

    hdf5_path = "graph.hdf5"
    hdf5_file = tables.openFile(hdf5_path, mode='w')
    filters = tables.Filters(complevel=5, complib='blosc')
    dist_store = hdf5_file.createCArray(hdf5_file.root, 'dist',
            tables.Atom.from_dtype(dist.dtype),
            shape=dist.shape,
            filters=filters)
    nxtv_store = hdf5_file.createCArray(hdf5_file.root, 'nxtv',
            tables.Atom.from_dtype(nxtv.dtype),
            shape=nxtv.shape,
            filters=filters)

    dist_store[:] = dist
    nxtv_store[:] = nxtv

    hdf5_file.close()

    print "HDF5 file closed."


def load():

    print "Loading pickles."
    rider_arr = pickle.load(open('rider_arr.p', 'rb'))
    team_arr = pickle.load(open('team_arr.p', 'rb'))

    team_conn = pickle.load(open('team_conn.p', 'rb'))

    n = len(rider_arr)
    print n
    conv_mats(n)

    hdf5_path = "graph.hdf5"
    hdf5_file = tables.openFile(hdf5_path, mode='r')
    dist = hdf5_file.root.dist
    nxtv = hdf5_file.root.nxtv

    print dist
    print dist.shape
    print dist[0, 1]
    print rider_arr[0]
    print rider_arr[1]
    print rider_arr[0:100]

    pp = path(dist, nxtv, team_arr, team_conn, 0, 1)
    print pp
    for x in pp:
        print rider_arr[x]


def path(dist, nxtv, team_arr, conn, u, v):
    if nxtv[u][v] == -1:
        return []
    path = [u]
    prev = u
    while u != v:
        u = nxtv[u][v]
        print team_arr[conn[(prev, u)]][u'name']
        prev = u
        path.append(u)
    return path


if __name__ == "__main__":
    main()
    load()

