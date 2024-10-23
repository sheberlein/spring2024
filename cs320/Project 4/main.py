import pandas as pd
from flask import Flask, request, jsonify
import flask
import time
import edgar_utils
import io
import geopandas as gpd
import re
import zipfile
import csv
import os
from io import TextIOWrapper
import matplotlib
import matplotlib.pyplot as plt
from shapely.geometry import box
matplotlib.use('Agg')

app = Flask(__name__)

last_requests = {}
ip_list = []
abcounter = 0
a = 0
b = 0

@app.route('/')
def home():
    global abcounter
    global a
    global b
    with open("index.html") as f:
        html = f.read()
    if abcounter % 2 == 1 and abcounter < 10:
        # show version B
        html = html.replace('<a href = "donate.html">Donate</a>', '<a href = "donate.html?from=B">donate</a>')
    elif abcounter % 2 == 0 and abcounter < 10:
        # show version A
        html = html.replace('<a href = "donate.html">Donate</a>', '<a href = "donate.html?from=A">DONATE</a>')
    else:
        if a > b:
            # A is better, so show version A from now on
            html = html.replace('<a href = "donate.html">Donate</a>', '<a href = "donate.html?from=A">DONATE</a>')
        else:
            # B is better, so show version B from now on
            html = html.replace('<a href = "donate.html">Donate</a>', '<a href = "donate.html?from=B">donate</a>')
    abcounter += 1
    return html

@app.route('/donate.html')
def donate_html():
    global a
    global b
    url = flask.request.args.get("from")
    if abcounter < 10 and url == "A":
        a += 1
    elif abcounter < 10 and url == "B":
        b += 1
    return "<h1>{}<h1>".format("Please give us money, we are poor Data Science students!")
    

@app.route('/browse.html')
def browse_html():
    csv = pd.read_csv("server_log.zip", compression="zip")
    html = csv[:500].to_html()
    return "<h1>Browse first 500 rows of rows.csv</h1><html>{}<html>".format(html)

@app.route('/analysis.html')
def analysis_html():
    string = """<p>Q1: how many filings have been accessed by the top ten IPs?</p>
    <p>111</p>
    <p>Q2: what is the distribution of SIC codes for the filings in docs.zip?</p>
    <p>222</p>
    <p>Q3: what are the most commonly seen street addresses?</p>
    <p>333</p>
    <h4>Dashboard: geographic plotting of postal code</h4>
    <img src="/dashboard.svg">
    """
    
    # question 1
    ips = pd.read_csv("server_log.zip", compression="zip")
    s1 = ips.to_dict()
    s2 = pd.Series(s1["ip"])
    
    # get the counts of each ip, sort it
    value_counts = s2.value_counts()
    s3 = pd.Series(value_counts.values, index=value_counts.index)
    s4 = s3.sort_values()
    
    # get the top 10 values
    top_10 = s4[-10:]
    
    # sort the dictionary by the values
    dicty_sort = {}
    for key, val in sorted(top_10.items(), key=lambda i: i[1], reverse=True):
        dicty_sort[key] = val
    
    # update the string to return
    string = string.replace("111", f"{dicty_sort}")
    
    
    # question 2
    dictionary = {}
    forq3 = {}
    with zipfile.ZipFile("docs.zip", "r") as z:
        files = z.namelist()
        for name in files:
            with z.open(name) as f:
                content = f.read().decode("utf-8")
                dictionary[name] = edgar_utils.Filing(content).sic
                forq3[name] = edgar_utils.Filing(content)
    
    filt = {}
    for key, val in dictionary.items():
        if val != None:
            filt[key] = val
    filt_series = pd.Series(filt)
    val_counts = filt_series.value_counts()
    new_series = pd.Series(val_counts.values, index = val_counts.index)
    sorted_series = new_series.sort_values(ascending=True)
    
    # convert to a dictionary
    top_10_2 = sorted_series.to_dict()
    
    # sort by value first, then key
    top_10_list = sorted(top_10_2.items(), key=lambda x: (x[1],x[0]), reverse=True)[:10]
    
    # get it back to a dictionary format
    top_10_return = {}
    for key, val in top_10_list:
        top_10_return[key] = val
    top_10_return
        
    string = string.replace("222", f"{top_10_return}")
    
    # question 3
    zf = zipfile.ZipFile("server_log.zip")
    f = zf.open("rows.csv")
    reader = csv.DictReader(TextIOWrapper(f))
    
    listy = []
    for row in reader:
        path = str(row["cik"]).replace(".0", "") + "/" + str(row["accession"]) + "/" + str(row["extention"])
        listy.append(path)
    new_dict = {}
    for filename in listy:
        if filename in forq3.keys():
            for address in forq3[filename].addresses:
                if address not in new_dict:
                    new_dict[address] = 1
                else:
                    new_dict[address] += 1
    new_dict2 = {}
    for address in new_dict:
        if new_dict[address] >= 300:
            new_dict2[address] = new_dict[address]
    
    string = string.replace("333", f"{new_dict2}")
    
    return string

@app.route("/dashboard.svg")
def dashboard_svg():
    # make the gdf
    gdf = gpd.read_file("locations.geojson")
    fig, ax = plt.subplots()
    ax.set_axis_off()
    
    gdf['postalcode'] = gdf['address'].str.findall(r'(\d{5})[-\d{4}]?').apply(lambda val: val[0] if val else None)
    
    # drop all of the none values, convert to an integer
    gdf["postalcode"] = gdf["postalcode"].fillna(0)
    gdf["postalcode"] = gdf["postalcode"].astype(int)
    
    # only take the postal codes between 25000 and 65000
    gdf = gdf[(gdf['postalcode'] >= 25000)]
    gdf = gdf[(gdf['postalcode'] <= 65000)]
    
    # america box
    america_window = box(-95, 25, -60, 50)
    
    shape = gpd.read_file('shapes/cb_2018_us_state_20m.shp')
    
    # cropping to the right latitudes
    gdf = gdf.cx[-95:-60, 25:50]
    shape = shape.intersection(america_window)
    
    # change the coordinate reference system
    shape = shape.to_crs("epsg:2022")
    gdf = gdf.to_crs("epsg:2022")
    
    # plot
    shape.plot(ax=ax, facecolor="lightgray")
    gdf.plot(ax=ax, column = "postalcode", legend = True, cmap="RdBu",)
    
    # save file
    f = io.StringIO()
    fig.savefig("dashboard.svg", format="svg")
    fig.savefig(f, format="svg")
    plt.close(fig)
    return flask.Response(f.getvalue(), headers={"Content-type": "image/svg+xml"})


@app.route('/browse.json')
def browse_json():
    csv = pd.read_csv("server_log.zip", compression="zip")
    dicty = csv[:500].to_dict()
    
    # only allow 1 request per minute
    global last_requests
    global ip_list
    address = request.remote_addr
    if address in last_requests:
        last_request_time = time.time() - last_requests[address]
        if last_request_time < 60:
            return flask.Response("<b>go away</b>", status=429, headers={"Retry-After": "60"})
    last_requests[address] = time.time()
    ip_list.append(address)
    return jsonify(dicty)
    
@app.route('/visitors.json')
def visiters_json():
    global ip_list
    return ip_list
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.
