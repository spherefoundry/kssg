import json
import os.path
import sys
from argparse import ArgumentParser
import traceback

from .config import Config
from .generator import Generator


def command_init():
    config_dict = {
        "src": "src",
        "output": "output",
        "title": "Your Title",
        "base_url": "https://example.com",
    }

    if os.path.exists(Config.workspace_config_file_path()):
        raise Exception(f"Workspace already has an config file. Skipping initialization.")

    with open(Config.workspace_config_file_path(), "w") as fp:
        json.dump(config_dict, fp, indent=4)

    os.makedirs(os.path.join(os.getcwd(), config_dict["src"]), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), config_dict["output"]), exist_ok=True)


def command_build(generator: Generator):
    generator.build()


def command_clean(generator: Generator):
    generator.clean()


def command_rebuild(generator: Generator):
    generator.clean()
    generator.build()


def command_watch(generator: Generator):
    generator.watch()


def run():
    parser = ArgumentParser(
        description='Build static site',
        prog='kssg'
    )

    commands_subparsers = parser.add_subparsers(
        help="Commands",
        required=True,
        metavar="<command>",
        title="Commands",
    )

    init_parser = commands_subparsers.add_parser(
        'init',
        help="Initiate a workspace"
    )
    init_parser.set_defaults(
        func=command_init,
        clean_command=True
    )

    build_parser = commands_subparsers.add_parser(
        'build',
        help="Build the site"
    )
    build_parser.set_defaults(
        func=command_build
    )

    clean_parser = commands_subparsers.add_parser(
        'clean',
        help="Delete any previous build results"
    )
    clean_parser.set_defaults(
        func=command_clean
    )

    rebuild_parser = commands_subparsers.add_parser(
        'rebuild',
        help="Shortcut for clean+build"
    )
    rebuild_parser.set_defaults(
        func=command_rebuild
    )

    watch_parser = commands_subparsers.add_parser(
        'watch',
        help="Automatically build the site on source file modification and reload in the browser"
    )
    watch_parser.set_defaults(
        func=command_watch
    )

    args = parser.parse_args()
    if "func" not in vars(args):
        parser.print_help()
        exit(0)
    try:
        if "clean_command" in vars(args) and args.clean_command:
            args.func()
        else:
            config = Config.load_from_workspace()
            generator = Generator(config)
            args.func(generator)
    except Exception as exc:
        print(traceback.format_exc(), file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    run()
