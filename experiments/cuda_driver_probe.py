"""Data-free low-level CUDA driver probe for a scheduler allocation."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path
from typing import Any


def _error_text(lib: Any, code: int) -> tuple[str | None, str | None]:
    name = ctypes.c_char_p()
    description = ctypes.c_char_p()
    try:
        lib.cuGetErrorName(code, ctypes.byref(name))
        lib.cuGetErrorString(code, ctypes.byref(description))
    except (AttributeError, OSError):
        return None, None
    return (
        name.value.decode("utf-8", errors="replace") if name.value else None,
        description.value.decode("utf-8", errors="replace") if description.value else None,
    )


def probe_cuda_driver() -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "aurora.cuda_driver_probe.v1",
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "library": "libcuda.so.1",
        "library_loaded": False,
        "cu_init_code": None,
        "cu_init_error_name": None,
        "cu_init_error_string": None,
        "device_count_code": None,
        "device_count": None,
        "probe_pass": False,
    }
    try:
        lib = ctypes.CDLL("libcuda.so.1")
    except OSError as error:
        result["load_error"] = str(error)
        return result

    result["library_loaded"] = True
    lib.cuInit.argtypes = [ctypes.c_uint]
    lib.cuInit.restype = ctypes.c_int
    init_code = int(lib.cuInit(0))
    result["cu_init_code"] = init_code
    name, description = _error_text(lib, init_code)
    result["cu_init_error_name"] = name
    result["cu_init_error_string"] = description
    if init_code != 0:
        return result

    lib.cuDeviceGetCount.argtypes = [ctypes.POINTER(ctypes.c_int)]
    lib.cuDeviceGetCount.restype = ctypes.c_int
    count = ctypes.c_int()
    count_code = int(lib.cuDeviceGetCount(ctypes.byref(count)))
    result["device_count_code"] = count_code
    result["device_count"] = int(count.value)
    result["probe_pass"] = count_code == 0 and count.value > 0
    return result


def write_atomic(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = probe_cuda_driver()
    write_atomic(args.output, result)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["probe_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
