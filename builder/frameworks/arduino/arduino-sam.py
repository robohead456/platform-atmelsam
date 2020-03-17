# Copyright 2020-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://arduino.cc/en/Reference/HomePage
"""

from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("framework-arduino-sam")
if board.get("build.core", "").lower() != "arduino":
    FRAMEWORK_DIR += "-%s" % board.get("build.core")
SYSTEM_DIR = join(FRAMEWORK_DIR, "system")

assert isdir(SYSTEM_DIR)
assert isdir(FRAMEWORK_DIR)

env.SConscript("arduino-common.py")

env.Append(
    CPPPATH=[
        join(SYSTEM_DIR, "libsam"),
        join(SYSTEM_DIR, "CMSIS", "CMSIS", "Include"),
        join(SYSTEM_DIR, "CMSIS", "Device", "ATMEL")
    ],

    LINKFLAGS=[
        "-Wl,--entry=Reset_Handler", "-u", "_sbrk", "-u", "link", "-u",
        "_close", "-u", "_fstat", "-u", "_isatty", "-u", "_lseek", "-u",
        "_read", "-u", "_write", "-u", "_exit", "-u", "kill",
        "-u", "_getpid"
    ],

    LIBS=["sam_sam3x8e_gcc_rel", "gcc"]
)

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:]
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    variants_dir = join(
        "$PROJECT_DIR", board.get("build.variants_dir")) if board.get(
            "build.variants_dir", "") else join(FRAMEWORK_DIR, "variants")
    env.Append(
        CPPPATH=[
            join(variants_dir, board.get("build.variant"))
        ],

        LIBPATH=[
            join(variants_dir, board.get("build.variant"))
        ],
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(variants_dir, board.get("build.variant"))
    ))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", "arduino")
))

env.Prepend(LIBS=libs)
