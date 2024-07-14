import subprocess
import sys
from pathlib import Path

from colorama import Fore
from sqlalchemy import select

from larch import LARCH_PROG_DIR
from larch.database.local import LocalPackage, local_db_engine


def run_by_name(is_detached, name, args_list):
    with local_db_engine.connect() as connection:
        prog = connection.execute(
            select(LocalPackage).where(LocalPackage.c.name == name)
        ).one_or_none()

    if prog is None:
        print(Fore.RED + f"Package '{name}' does not exist, stopping")
        sys.exit(1)

    if prog.executable is None:
        print(Fore.RED + f"No executable registered for the package '{name}'")
        sys.exit(1)

    executable_path = Path(LARCH_PROG_DIR / name) / prog.executable

    if is_detached:
        subprocess.Popen([executable_path, *args_list])
    else:
        subprocess.run([executable_path, *args_list])
