# KSSG - Kedracki Static Site Generator

An extremely simple static site generator writen in Python. 

## Disclaimer

I have writen this tool to support my various online presences. Although it is released under the MIT license, I don't 
intend to make it a proper OSS project. That is, my needs will always take precedence. Backward compatibility may break 
at any moment. For the same reason this is not published on PyPi.

If you decide to use KSSG please consider pinning to a specific version tag. It can be done with `git+https`:  

```shell
pip install git+https://https://github.com/spherefoundry/kssg.git@<tag>
```

## Usage

Create a venv:

```shell
python -m venv <path_to_your_venv>
```

Activate the venv 

```shell
source <path_to_your_venv>/bin/activate
```

Install KSSG

```shell
pip install git+https://https://github.com/spherefoundry/kssg.git
```

OR (even better) pin to specific version <tag> 

```shell
pip install git+https://https://github.com/spherefoundry/kssg.git@<tag>
```

Initialize workspace

```shell
kssg init
```

Modify the kssg.json file

```json
{
    "src": "src",
    "output": "output",
    "domain": "https://example.com"
}
```

Optional settings (with defaults):

```json
{
  "serverHost": "localhost",
  "serverPort": 8001,
  "server_open_browser_tab": false
}
```

