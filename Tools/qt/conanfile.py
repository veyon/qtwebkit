# Copyright (C) 2020 Konstantin Tokarev <annulen@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from conans import ConanFile, CMake, tools
import os
import shlex
import argparse


class QtWebKitConan(ConanFile):
    name = "qtwebkit"
    version = "5.212.0-alpha4"
    license = "LGPL-2.0-or-later, LGPL-2.1-or-later, BSD-2-Clause"
    url = "https://github.com/qtwebkit/qtwebkit"
    description = "Qt port of WebKit"
    topics = ("qt", "browser-engine", "webkit", "qt5", "qml", "qtwebkit")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "virtualenv", "txt"
    exports_sources = "../../*"
    no_copy_source = True
    requires = (
        "libjpeg-turbo/2.0.3@qtproject/stable",
        "libpng/1.6.37",
        "libwebp/1.1.0"
    )
    default_options = {
        "icu:shared": True,
        "icu:data_packaging": "library",

        "libxml2:shared": True,
        "libxml2:iconv": False,
        "libxml2:icu": True,
        "libxml2:zlib": False,

        "libxslt:shared": True,

        "libjpeg-turbo:shared": False,
        "zlib:shared": False,
        "libpng:shared": False,
        "sqlite3:shared": False,
        "libwebp:shared": False
    }

    def build_requirements(self):
        if self.settings.os == 'Linux':
            if not tools.which('pkg-config'):
                self.build_requires(
                    'pkg-config_installer/0.29.2@bincrafters/stable')

        # gperf python perl bison ruby flex
        if not tools.which("gperf"):
            self.build_requires("gperf_installer/3.1@conan/stable")
        if not tools.which("perl"):
            self.build_requires("strawberryperl/5.30.0.1")
        if not tools.which("ruby"):
            self.build_requires("ruby_installer/2.6.3@bincrafters/stable")
        if not tools.which("bison"):
            self.build_requires("bison_installer/3.3.2@bincrafters/stable")
        if not tools.which("flex"):
            self.build_requires("flex_installer/2.6.4@bincrafters/stable")
        if not tools.which("ninja"):
            self.build_requires("ninja/1.9.0")
        if not tools.which("cmake"):
            self.build_requires("cmake/3.16.4")

    def requirements(self):
        # TODO: Handle case when custom ICU is needed (AppStore etc., MACOS_USE_SYSTEM_ICU=OFF in CMake)
        if self.settings.os != 'Macos':
            self.requires("icu/65.1@qtproject/stable")
            self.requires("libxml2/2.9.10@qtproject/stable")
            self.requires("libxslt/1.1.34@qtproject/stable")
            self.requires("zlib/1.2.11")
            self.requires("sqlite3/3.31.1")

    def build(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.generator = "Ninja"
        cmake.verbose = False
        cmake.definitions["QT_CONAN_DIR"] = self.build_folder
        # QtWebKit installation requires conanfile.txt in build directory
        self.write_imports()

        # if self.options.use_ccache:
        #    cmake.definitions["CMAKE_C_COMPILER_LAUNCHER"] = "ccache"
        #    cmake.definitions["CMAKE_CXX_COMPILER_LAUNCHER"] = "ccache"

        if "QTDIR" in os.environ:
            cmake.definitions["Qt5_DIR"] = os.path.join(
                os.environ["QTDIR"], "lib", "cmake", "Qt5")
            print("Qt5 directory:" + cmake.definitions["Qt5_DIR"])

        if "CMAKEFLAGS" in os.environ:
            cmake_flags = shlex.split(os.environ["CMAKEFLAGS"])
        else:
            cmake_flags = None

        if "NINJAFLAGS" in os.environ:
            parser = argparse.ArgumentParser()
            parser.add_argument('-j', default=None, type=int)
            jarg, ninja_flags = parser.parse_known_args(
                shlex.split(os.environ["NINJAFLAGS"]))
            if jarg.j:
                os.environ['CONAN_CPU_COUNT'] = str(jarg.j)
            ninja_flags.insert(0, '--')
        else:
            ninja_flags = None

        print(self.source_folder)
        print()
        print(self.build_folder)

        cmake.configure(args=cmake_flags)
        cmake.build(args=ninja_flags)
        cmake.install()

    # QtWebKit installation requires conanfile.txt in build directory, so we generate it here
    # Should be kept in sync with imports()
    def write_imports(self):
        conanfile = open(os.path.join(self.build_folder, "conanfile.txt"), "w")
        conanfile.write("[imports]\n")

        if self.settings.os == 'Windows':
            conanfile.write("bin, icudt65.dll -> ./bin\n")
            conanfile.write("bin, icuin65.dll -> ./bin\n")
            conanfile.write("bin, icuuc65.dll -> ./bin\n")
            # Visual Studio
            conanfile.write("bin, libxml2.dll -> ./bin\n")
            conanfile.write("bin, libxslt.dll -> ./bin\n")
            # MinGW
            conanfile.write("bin, libxml2-2.dll -> ./bin\n")
            conanfile.write("bin, libxslt-1.dll -> ./bin\n")

        conanfile.close()

    def imports(self):
        if self.settings.os == 'Windows':
            self.copy("icudt65.dll", "./bin", "bin")
            self.copy("icuin65.dll", "./bin", "bin")
            self.copy("icuuc65.dll", "./bin", "bin")
            # Visual Studio
            self.copy("libxml2.dll", "./bin", "bin")
            self.copy("libxslt.dll", "./bin", "bin")
            # MinGW
            self.copy("libxml2-2.dll", "./bin", "bin")
            self.copy("libxml2-2.dll", "./bin", "bin")

    def package(self):
        pass

    def package_info(self):
        pass
