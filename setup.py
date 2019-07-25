import setuptools
from setuptools.extension import Extension
from setuptools.command.test import test
from distutils.command import clean
from distutils.file_util import copy_file
from distutils.dir_util import mkpath, remove_tree, copy_tree
from distutils import log
from Cython.Build import cythonize
from sage.env import sage_include_directories, cython_aliases, UNAME
import os
import sys

UPSTREAM_TAR_URL = "https://www-polsys.lip6.fr/~jcf/FGb/C/@downloads/call_FGb6.maclinux.x64.tar.gz"
UPSTREAM_TAR_BASEDIR = "call_FGb"

cwd = os.path.abspath(os.getcwd())
SRC = "fgb_sage"
VERSION = open("VERSION").read().strip()

def md5sum(filename):
    import hashlib
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()

class BuildLibfgbCommand(setuptools.Command):
    description = "download, extract and patch libfgb files"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        log.info("Loading checksums.")
        libfgb_pkgdir = "pkgs/libfgb"
        checksums_file = os.path.join(libfgb_pkgdir, "checksums.ini")
        with open(checksums_file, 'r') as f:
            checksums = dict(s.split('=') for s in f.read().split('\n') if s)

        log.info("Checking if upstream tar file exists.")
        if not os.path.exists("upstream"):
            mkpath("upstream")
        libfgb_file = os.path.join("upstream", checksums["tarball"])
        if not os.path.exists(libfgb_file):
            log.warn("File %s does not exist. Attempting to download from %s." % (libfgb_file, UPSTREAM_TAR_URL))
            # We use curl to avoid [SSL: CERTIFICATE_VERIFY_FAILED] errors
            os.system("curl --insecure --create-dirs -o %s %s" % (libfgb_file, UPSTREAM_TAR_URL))
            if not os.path.exists(libfgb_file):
                log.error("""Download failed. You may wish to download the file "%s" manually from "%s" and place it in the "upstream/" directory.""" %
                        (checksums["tarball"], UPSTREAM_TAR_URL))
                sys.exit(1)
        if md5sum(libfgb_file) != checksums["md5"]:
            log.error("Checksum for file %s is different." % libfgb_file)
            sys.exit(1)

        log.info("Creating directories.")
        if os.path.exists("local"):
            remove_tree("local")
        mkpath("local/include")
        mkpath("local/lib")
        tmpdir = "local/var/tmp"
        mkpath(tmpdir)

        log.info("Extracting tar file.")
        import tarfile
        tar = tarfile.open(libfgb_file)
        tar.extractall(tmpdir)
        tar.close()
        libfgb_builddir = os.path.join(tmpdir, UPSTREAM_TAR_BASEDIR)
        if not os.path.exists(libfgb_builddir):
            log.error("Failed to extract files properly.")
            sys.exit(1)

        log.info("Applying patches.")
        os.chdir(libfgb_builddir)
        if os.system("sage-apply-patches %s" % os.path.join(cwd, libfgb_pkgdir, "patches")):
            log.error("Failed to apply patches.")
            sys.exit(1)
        os.chdir(cwd)

        log.info("Copying include and lib files.")
        if UNAME == "Darwin":
            FGB_LIBDIR = "macosx"
        elif UNAME == "Linux":
            FGB_LIBDIR = "x64"
        else:
            log.error("Error installing libfgb: libfgb is not available for this platform.")
            sys.exit(1)
        for f in ["nv/int/protocol_maple.h", "nv/maple/C/call_fgb.h", "nv/maple/C/call_fgb_basic.h"]:
            copy_file(os.path.join(libfgb_builddir, f), "local/include")
        copy_tree(os.path.join(libfgb_builddir, "nv/protocol"), "local/include")
        copy_tree(os.path.join(libfgb_builddir, "nv/maple/C", FGB_LIBDIR), "local/lib")

class TestCommand(test):
    def run_tests(self):
        errno = os.system("sage -t --force-lib --optional=sage,fgb_sage %s" % SRC)
        if errno != 0:
            sys.exit(1)

class CleanCommand(clean.clean):
    def run(self):
        if os.path.exists("local"):
            remove_tree("local")
        clean.clean.run(self)

class BuildExtCommand(setuptools.command.build_ext.build_ext):
    def run(self):
        self.run_command('build_libfgb')
        setuptools.command.build_ext.build_ext.run(self)

PYX_FILES = [("_fgb_sage_int", 2), ("_fgb_sage_modp", 1)]
pyx_src = os.path.join(SRC, PYX_FILES[0][0] + ".pyx")
pyx_dst = os.path.join(SRC, PYX_FILES[1][0] + ".pyx")

# We always copy the source files here, as they are needed for ext_modules below
log.info("Copying %s -> %s" % (pyx_src, pyx_dst))
copy_file(pyx_src, pyx_dst, update=True)
if not os.path.exists(pyx_dst):
    log.error("Failed to generate %s" % pyx_dst)
    sys.exit(1)
# This is a workaround for Ubuntu on Travis where update=True results in empty
# files
if os.path.getsize(pyx_dst) == 0:
    log.warn("Using fallback since target is empty: %s" % pyx_dst)
    copy_file(pyx_src, pyx_dst, update=False)
    if not os.path.exists(pyx_dst) or os.path.getsize(pyx_dst) == 0:
        log.error("Failed to generate %s" % pyx_dst)
        sys.exit(1)

ext_modules = [
    cythonize(
        [Extension("fgb_sage." + name,
            include_dirs=["local/include"] + sage_include_directories(),
            library_dirs=["local/lib"],
            libraries=["fgb", "fgbexp", "gb", "gbexp", "minpoly", "minpolyvgf", "gmp", "m"],
            extra_compile_args=["-std=c++11", "-fopenmp"],
            extra_link_args=["-fopenmp"],
            define_macros=[
                ("LIBMODE", libmode),
                ("FGB_MAC", 1 if UNAME == 'Darwin' else 0),
                ("FGB_MAC_MAX_INPUT", 100000)],
            sources=[os.path.join(SRC, name + ".pyx")]
        )],
        compile_time_env=dict(
            PY_LIBMODE=libmode,
            PY_FGB_MAC=(UNAME == 'Darwin')),
        compiler_directives=dict(language_level=2),
        annotate=False,
        aliases=cython_aliases()
    )[0]
    for (name, libmode) in PYX_FILES]

setuptools.setup(
    cmdclass={
        'build_libfgb': BuildLibfgbCommand,
        'build_ext': BuildExtCommand,
        'test': TestCommand,
        'clean': CleanCommand,
        },
    name="fgb_sage",
    version=VERSION,
    packages=["fgb_sage"],
    ext_modules=ext_modules)
