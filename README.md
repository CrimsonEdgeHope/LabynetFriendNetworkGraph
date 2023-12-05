# LabynetFriendNetworkGraph

A script that helps you fetch and analyse a whole friendship relations of a community of people from `laby.net`

Prerequisites:

- Python 3.10
- Python packages in `requirements.txt`

Run command:
```shell
pip install -r requirements.txt
python LabynetFriendNetworkGraph.py
```

After the script finishes job, a json file that contains all fetched data will be saved to `result` directory, which is useful for graph generation and data analysis.

## Config

| Key              | Description                                    |
|------------------|------------------------------------------------|
| http_proxy       | A http proxy                                   |
| https_proxy      | A https proxy                                  |
| maximum_requests | How many requests can be sent in total at most |


Example:

```json
{
    "http_proxy": "socks5://127.0.0.1:1080",
    "https_proxy": "socks5://127.0.0.1:1080",
    "maximum_requests": 5
}
```

## License

Licensed under WTFPL

## Reference

- [Laby.net API documentation](https://laby.net/api/docs)

## Trivial thoughts

Together, a community can form inconceivable power, unexpectedly in large scale with a decent number of connections.

Take [Action run No.7096370784](https://github.com/CrimsonEdgeHope/LabynetFriendNetworkGraph/actions/runs/7096370784) as an example,
according to the generated json result, the script designed to be run on Windows successfully tracked 8308 Minecraft players
that have ever registered on `laby.net`, after 500 web requests, starting from a seem-to-be insignificant spot.

```pycon
>>> import json
>>> import os
>>> _p = os.path.join('result', '2023-12-05-05-38-13.json')
>>> with open(_p, 'r') as f:
...     _d = json.loads(f.read())
...
>>> print(_d['metadata'])
{'created_at_unix': 1701754693.627322, 'request_headers': {'host': 'laby.net', 'user-agent': 'Mozilla/5.0 (compatible; LabynetFriendNetworkGraph/beta-0.1.1; +https://github.com/CrimsonEdgeHope)', 'accept': '*/*'}, 'config': {'maximum_requests': 500, 'automate': '1', 'start_spot': '22500b81-e889-4367-b83c-24c52914e2de', 'debug': True, 'import_json': None}}
>>> print(len(_d['leftovers']))
7808
>>> print(len(_d['data']['edges']))
14598
>>> print(len(_d['data']['nodes']))
8308
>>> print(len(_d['errored']['forbid_out']))
206
>>> print(len(_d['data']['uuid_to_ign']))
8308
>>> print(len(_d['errored']['error_out']))
0
>>>
```

As a matter of fact, to be more precise, 206 of 8308 hide their full friendship data (`laby.net` itself returns 403 instead of Cloudflare), 14598 public friendship connections on `laby.net` discovered in these 8308.
In addition, 7808 players are yet to be tracked due to limitation of requests. Should the number of requests be raised to a higher value, more data with certainty, which in total means 16116 Minecraft players on `laby.net`, and more than 14598 connections.

Personally, in my process of manual analysis, some similar in-game names should come to my view ever once again. Even following the death
of a once-with-great-reputation Minecraft minigame server in May 2023, ghosts haunt in minds, disturbing, sick, unpleasant.
Power can be either good or bad, it depends on the one that wields.
Rather than that, it applies to literally everything. Is it able to contribute to its prosperity? Yes. It's also able to, either, contribute to its death.
A community of people, maybe dozens, had chosen the latter, in exchange for isolated islands deep in shady corners under sea of glacier, nowhere to seek light.

However, no worry. We dive in for a happy time, we've made it. We dive in dev platforms for greater, meaning-filled purposes.
We either move on to grind on retrospection, or to look forward and forget petty past.

Dive in, wear mask, gather data, be the one who's in control.
