# LabynetFriendNetworkGraph

A script that helps you fetch and analyse a whole friendship relations of a community of people from `laby.net`

After the script finishes job, a json file that contains all fetched data will be saved to `result` directory, which is useful for graph generation and data analysis.
In addition, there are some helpful scripts providing summarization, and CQL query generation suitable for Neo4j.

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

## Config

Create `config.json` in project's root directory:

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

- [Laby.net API documentation](https://web.archive.org/web/20211001164932/https://laby.net/api/docs)
