import glob
import os
import shutil
import subprocess

from setuptools import setup
from setuptools.command.build_py import build_py

ROOT = os.path.dirname(os.path.abspath(__file__))
BFF_DIR = os.path.join(ROOT, "biofile-finder")
DIST_DIR = os.path.join(
    ROOT, "omero_biofilefinder", "static", "omero_biofilefinder", "dist"
)


def build_bff(announce=print):
    if not os.path.exists(os.path.join(BFF_DIR, "package.json")):
        # e.g. building a wheel from an sdist: use the bundled assets
        announce("biofile-finder submodule not found: using existing dist assets")
        return
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError(
            "npm is required to build the BioFile Finder app but was not "
            "found on PATH. Install Node.js/npm and try again."
        )
    subprocess.check_call([npm, "install"], cwd=BFF_DIR)
    subprocess.check_call(
        [npm, "--prefix", "packages/web", "run", "build"], cwd=BFF_DIR
    )
    os.makedirs(DIST_DIR, exist_ok=True)
    for old in glob.glob(os.path.join(DIST_DIR, "*")):
        if os.path.isdir(old):
            shutil.rmtree(old)
        else:
            os.remove(old)
    for built in glob.glob(os.path.join(BFF_DIR, "packages", "web", "dist", "*")):
        if os.path.isdir(built):
            shutil.copytree(built, os.path.join(DIST_DIR, os.path.basename(built)))
        else:
            shutil.copy2(built, DIST_DIR)


class BuildPyWithBff(build_py):
    """Build the BioFile Finder app and copy its assets before packaging."""

    def run(self):
        build_bff(self.announce)
        super().run()


cmdclass = {"build_py": BuildPyWithBff}

try:
    # pip install -e . does not call build_py.run(), so hook it as well
    from setuptools.command.editable_wheel import editable_wheel

    class EditableWheelWithBff(editable_wheel):
        def run(self):
            build_bff(self.announce)
            super().run()

    cmdclass["editable_wheel"] = EditableWheelWithBff
except ImportError:  # setuptools < 64
    pass

setup(cmdclass=cmdclass)
