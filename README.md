# LabynetFriendNetworkGraph

A script that helps you fetch and analyse a whole friendship relations of a community of people from `laby.net`

## Usage

Prerequisites:

- Python 3.10
- Python packages in `requirements.txt`

Run command:
```shell
pip install -r requirements.txt
python LabynetFriendNetworkGraph.py
```

Follow prompts, tell the script the place to start from, then sit and have a cup of Java.

After the script finishes job, a json file that contains all fetched data will be saved to `result` directory, which is useful for graph generation and data analysis.

### Config

Create `config.json` in project's root directory. (json5 allows comments while json does not.)

```json5
{
  "debug": false,  // Enable debugging message
  "proxy": {
    "http_proxy": "",   // HTTP proxy
    "https_proxy": ""   // HTTPS proxy
  },
  "automate": null,     // Run script without interactive prompts. "1" to start crawling, "2" to import a copy of result json.
  "import_json": null,  // A copy of result json in result directory to be imported. Only filename, no path. Used as default value.
  "crawler": {
    "crawling_method": "2",  // "1": Depth-first crawling. "2": Breadth-first crawling.
    "maximum_requests": 10,  // How many requests can the crawler send to laby.net, including failures.
    "start_spot": null       // A Minecraft player's UUID to start from. Used as default value.
  },
  "static_html_export": {
    "html": "graph.html",   // Filename of static html file that shows a graph.
    "graph_width": 1920,    // Width in px
    "graph_height": 1080    // Height in px
  }
}
```

Example config:
```json
{
  "debug": true,
  "proxy": {
    "http_proxy": "",
    "https_proxy": ""
  },
  "import_json": null,
  "automate": "1",
  "crawler": {
    "crawling_method": "2",
    "maximum_requests": 10,
    "start_spot": "7659cedb-c9c1-4f28-b966-19823fd8666b"
  },
  "static_html_export": {
    "html": "graph.html",
    "graph_width": 1920,
    "graph_height": 1080
  }
}
```

### Tools

There are also some helpful scripts providing summarization, and CQL query generation suitable for Neo4j.

- Summarization:

```shell
python result_json_summarization.py result_json_thats_in_result_dir.json
```

- CQL generation:

```shell
python result_json_to_neo4j_cql.py result_json_thats_in_result_dir.json
```


## Gallery

Result json and CQL:

![](https://assets.app.crimsonedgehope.warpedinnether.top:65499/LabynetFriendNetworkGraph-2.png)

Neo4j database:

![](https://assets.app.crimsonedgehope.warpedinnether.top:65499/LabynetFriendNetworkGraph-1.png)

## License

Licensed under WTFPL

## Reference

- [Laby.net API documentation](https://web.archive.org/web/20211001164932/https://laby.net/api/docs)
