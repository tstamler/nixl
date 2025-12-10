# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

pybind_dep = dependency('pybind11')

nixl_dep = declare_dependency(link_with: nixl_lib, include_directories: nixl_inc_dirs)

py = import('python').find_installation('python3', pure: false)

if cuda_dep.found()
    cuda_dependencies = [cuda_dep]
    device_api_inc = [nixl_gpu_inc_dirs]
    device_api_dep = [ucx_dep, doca_gpunetio_dep]
else
    cuda_dependencies = []
    device_api_inc = []
    device_api_dep = []
endif

py.extension_module('_bindings',
           'nixl_bindings.cu',
           subdir: (cuda_wheel_dir),
           dependencies: [nixl_dep, serdes_interface, pybind_dep, cuda_dependencies, device_api_dep],
           include_directories: [nixl_inc_dirs, utils_inc_dirs, device_api_inc],
           install: true)

py.extension_module('_utils',
           'nixl_utils.cpp',
           subdir: (cuda_wheel_dir),
           dependencies: [pybind_dep],
           install: true)

subdir('nixl-meta')
