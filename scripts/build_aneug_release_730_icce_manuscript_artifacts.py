#!/usr/bin/env python3
"""Build identifier-free ICCE tables, CSV files, and Figure 2 from terminal cells."""

from __future__ import annotations

import argparse

from aurora.aneug_release_730_icce_artifacts import (
    compile_manuscript_artifacts,
    load_artifact_inputs,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", required=True)
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--render-figure", action="store_true")
    arguments = parser.parse_args()
    inputs = load_artifact_inputs(arguments.input_manifest)
    compile_manuscript_artifacts(
        **inputs,
        output_directory=arguments.output_directory,
        render_figure=arguments.render_figure,
    )


if __name__ == "__main__":
    main()
