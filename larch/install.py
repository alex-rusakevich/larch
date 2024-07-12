from typing import List
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
from larch.passed_to_seed import join_path, unzip, copy
from larch.cli import progress_fetch
from larch import LARCH_TEMP, LARCH_PROG_DIR
from pathlib import Path
from larch.installed_db import db_add_new_program, db_program_exists
import shutil
import sys


def install_seed(seed: str):
    print(f"Installing '{seed}'...")
    seed_code = ""

    with open(seed, mode="r", encoding="utf8") as seed_file:
        seed_code = seed_file.read()

    loc = {}
    byte_code = compile_restricted(seed_code, "<inline>", "exec")
    exec(
        byte_code,
        {**safe_globals, "join_path": join_path, "unzip": unzip, "copy": copy},
        loc,
    )

    if db_program_exists(loc["NAME"]):
        print("Program '{}' already exists, stopping".format(loc["NAME"]))
        sys.exit(1)

    # region Preparing directories
    temp_dir = Path(LARCH_TEMP / loc["NAME"])
    dest_dir = Path(LARCH_PROG_DIR / loc["NAME"])

    if temp_dir.exists() and temp_dir.is_dir():
        shutil.rmtree(temp_dir)

    if dest_dir.exists() and dest_dir.is_dir():
        shutil.rmtree(dest_dir)

    Path.mkdir(temp_dir)
    Path.mkdir(dest_dir)
    # endregion

    for dest_file_name, download_url in loc["SOURCE"].items():
        progress_fetch(download_url, temp_dir / dest_file_name)

    executable_path = loc["install"](temp_dir, dest_dir)

    db_add_new_program(
        name=loc["NAME"],
        version=loc["VERSION"],
        description=loc["DESCRIPTION"],
        author=loc["AUTHOR"],
        maintainer=loc["MAINTAINER"],
        url=loc["URL"],
        license=loc["LICENSE"],
        executable_path=executable_path,
    )

    print(
        f"'{seed}' was installed successfully! The executable file is '{executable_path}'"
    )
    print("Removing temporary files...")
    shutil.rmtree(temp_dir)


def install_seeds(seeds: List[str]):
    for seed in seeds:
        install_seed(seed)


def install_pkg_names(pkg_names: List[str]):
    raise NotImplementedError()
