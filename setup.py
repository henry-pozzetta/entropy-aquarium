import os
import sys
from setuptools import setup

# --- Project scaffold configuration -----------------------------------------
PROJECT_STRUCTURE = {
    "data_streams": ["synthetic_stream.py"],
    "entropy_core": ["entropy_engine.py"],
    "frames": ["eeframe_generator.py"],
    "visualization": ["display_3d.py"],
    "sandbox": ["strategy_plugins.py"],
    "": ["run.py", "README.md", "requirements.txt"],
}

DEFAULT_REQUIREMENTS = """numpy\nscipy\nmatplotlib\n"""

DEFAULT_README = (
    "# Entropy Aquarium\n\n"
    "A live entropy visualization sandbox and demonstrator with real-time telemetry "
    "stream input, 3D entropy arrow display, and strategy prototyping features.\n"
)


def _write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def create_project_structure(base_dir: str = ".") -> None:
    """Create the initial folder/file scaffold. Safe to re-run (idempotent)."""
    created = []
    for folder, files in PROJECT_STRUCTURE.items():
        target_dir = os.path.join(base_dir, folder) if folder else base_dir
        if folder and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            created.append(f"dir: {target_dir}")
        for filename in files:
            full_path = os.path.join(target_dir, filename)
            if not os.path.exists(full_path):
                if filename == "requirements.txt":
                    _write_text(full_path, DEFAULT_REQUIREMENTS)
                elif filename == "README.md":
                    _write_text(full_path, DEFAULT_README)
                else:
                    stub = (
                        f"# {filename}\n\n"
                        "\"\"\"\n"
                        "Stub created by setup.py scaffold. Replace with implementation.\n"
                        "\"\"\"\n"
                    )
                    _write_text(full_path, stub)
                created.append(f"file: {full_path}")

    if created:
        print("Scaffold created:")
        for item in created:
            print("  -", item)
    else:
        print("Scaffold already present; nothing to create.")


if __name__ == "__main__":
    # When invoked directly (e.g., `python setup.py`), always run the scaffold.
    create_project_structure()

    # If setuptools commands are provided (e.g., develop/sdist/bdist_wheel), run setup().
    if len(sys.argv) > 1 and sys.argv[1] not in ("-c",):
        setup(
            name="entropy-aquarium",
            version="0.1.0",
            description="Entropy visualization sandbox and prototyping tool",
            author="henry-pozzetta",
            packages=[],  # to be populated once modules are packaged
            install_requires=["numpy", "scipy", "matplotlib"],
            include_package_data=True,
            zip_safe=False,
        )
