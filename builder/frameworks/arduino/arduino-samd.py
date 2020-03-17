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

BUILD_CORE = board.get("build.core", "").lower()

FRAMEWORK_DIR = platform.get_package_dir("framework-arduino-samd")
if BUILD_CORE != "arduino":
    FRAMEWORK_DIR += "-%s" % BUILD_CORE
CMSIS_DIR = platform.get_package_dir("framework-cmsis")
CMSIS_ATMEL_DIR = platform.get_package_dir("framework-cmsis-atmel")

assert all(isdir(d) for d in (FRAMEWORK_DIR, CMSIS_DIR, CMSIS_ATMEL_DIR))

env.SConscript("arduino-common.py")

env.Append(
    CPPPATH=[
        join(CMSIS_DIR, "CMSIS", "Include"),
        join(CMSIS_ATMEL_DIR, "CMSIS", "Device", "ATMEL")
    ],

    LIBPATH=[
        join(CMSIS_DIR, "CMSIS", "Lib", "GCC"),
    ],

    LINKFLAGS=[
        "--specs=nosys.specs",
        "--specs=nano.specs"
    ]
)

if board.get("build.cpu") == "cortex-m4":
    env.Prepend(
        CCFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16"
        ],

        LINKFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16"
        ],

        LIBS=["arm_cortexM4lf_math"]
    )
else:
    env.Prepend(
        LIBS=["arm_cortexM0l_math"]
    )

if BUILD_CORE == "adafruit":
    env.Append(
        CPPDEFINES=[
            ("USB_CONFIG_POWER", board.get("build.usb_power", 100))
        ],

        CCFLAGS=[
            "-Wno-expansion-to-defined"
        ],

        CPPPATH=[
            join(FRAMEWORK_DIR, "cores", "arduino", "TinyUSB"),
            join(FRAMEWORK_DIR, "cores", "arduino", "TinyUSB",
                 "Adafruit_TinyUSB_ArduinoCore"),
            join(FRAMEWORK_DIR, "cores", "arduino", "TinyUSB",
                 "Adafruit_TinyUSB_ArduinoCore", "tinyusb", "src")
        ]
    )

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:],
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
        CPPPATH=[join(variants_dir, board.get("build.variant"))]
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
