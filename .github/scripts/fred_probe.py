import urllib.request, urllib.error, json
out={}
for name,url in {"graph_csv":"https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE&cosd=2025-01-01",
                 "api_nokey":"https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&file_type=json"}.items():
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; AlphaGen Research; desk@alphagenresearch.com)"}),timeout=60)
        out[name]={"status":r.status,"head":r.read(200).decode("utf-8","replace")}
    except urllib.error.HTTPError as e:
        out[name]={"status":e.code,"head":e.read(200).decode("utf-8","replace")}
    except Exception as e:
        out[name]={"error":repr(e)[:200]}
json.dump(out,open("fred/_probe.json","w"),indent=1); print(out)
