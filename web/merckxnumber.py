# -*- coding: utf-8 -*-

import pickle
import tables
from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash, jsonify

import sys
import numpy as np

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.debug = False

rider_arr = pickle.load(open('rider_arr.p', 'rb'))
team_arr = pickle.load(open('team_arr.p', 'rb'))
team_conn = pickle.load(open('team_conn.p', 'rb'))

n = len(rider_arr)

hdf5_path = "graph.hdf5"
hdf5_file = tables.openFile(hdf5_path, mode='r')

dist = hdf5_file.root.dist
nxtv = hdf5_file.root.nxtv

def get_path(u, v):
    if u >= n:
        return []
    if v >= n:
        return []

    if nxtv[u][v] == -1:
        return []

    path = [int(u)]
    prev = u
    while u != v:
        u = nxtv[u][v]
        prev = u
        path.append(int(u))
    return path

@app.route('/')
@app.route('/home')
def front():
    return render_template('front.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/riders')
def riders_search():
    q = request.args.get('q').lower()
    qs = q.split(' ')
    res = rider_arr
    for q in qs:
        res = filter(lambda x: q in x['rider'].lower(), res)
    return jsonify(**{ 'riders': res })

@app.route('/graph.json')
def graph_data():
    conn = []
    riders = []
    ridx = {}
    for x, y in team_conn.keys():
        if int(team_arr[team_conn[(x, y)]]['year']) >= 2015:
            if x not in ridx.keys():
                ridx[x] = len(riders)
                riders.append(rider_arr[x])
            if y not in ridx.keys():
                ridx[y] = len(riders)
                riders.append(rider_arr[y])
            conn.append({ "source": ridx[x], "target": ridx[y] })

    return jsonify(**{ 'nodes': riders, 'links': conn })

@app.route('/graph')
def graph():
    return render_template('graph.html')

@app.route('/path/<int:u>/<int:v>')
def path(u, v):
    pr = get_path(u, v)

    riders = []
    teams = []
    
    prev = None
    for p in pr:
        if prev is not None:
            team = team_conn[(prev, p)]
            teams.append(team_arr[team])
        riders.append(rider_arr[p])
        prev = p

    return jsonify(**{ 'riders': riders, 'teams': teams })

if __name__ == '__main__':
    app.run()

