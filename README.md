# LabynetFriendNetworkGraph

This is just a simple script that helps you fetch and analyse a whole friendship relations of a community of people from `laby.net`

Prerequisites:

- Python 3.10
- Python packages in `requirements.txt`

Run command:
```shell
pip install -r requirements.txt
python LabynetFriendNetworkGraph.py
```

After the script finishes job, a json file that contains all fetched data will be written to `result` directory, and a html file that reveals a picture of visual graph will be generated. 

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

Licensed under WTFPL, you just do what the fuck you want with this script. No any formation of guarantee will be given.

## Reference

- [Laby.net API documentation](https://laby.net/api/docs)
