import json
import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    src_path: str
    output_path: str
    site_base_url: str
    site_title: str = ""
    template_extensions: List[str] = field(default_factory=lambda: ['.html'])
    posts_extensions: List[str] = field(default_factory=lambda: ['.md', '.markdown'])
    post_dir: str = '_posts'
    server_host: str = 'localhost'
    server_port: int = 8001
    server_open_browser_tab: bool = False

    @staticmethod
    def workspace_config_file_path():
        return os.path.join(os.getcwd(), 'kssg.json')

    @staticmethod
    def load_from_workspace():
        return Config.load_from_file(Config.workspace_config_file_path())

    @staticmethod
    def load_from_file(path: str) -> 'Config':
        if not os.path.exists(path):
            raise Exception(f"Config file missing at {path}")

        with open(path, "r") as fp:
            data = json.load(fp)

        kwargs = {}

        def get(dst_key: str, src_key: str, required: bool):
            value = data.get(src_key, None)
            if required and value is None:
                raise Exception(f"Config file is missing a value for {src_key}")

            if value is not None:
                kwargs[dst_key] = value

        get("src_path", "src", True)
        get("output_path", "output", True)
        get("site_title", "title", True)
        get("site_base_url", "base_url", True)

        get("server_host", "serverHost", False)
        get("server_port", "serverPort", False)
        get("server_open_browser_tab", "serverOpenBrowserTab", False)

        return Config(**kwargs)
