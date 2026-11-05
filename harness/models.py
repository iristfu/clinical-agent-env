"""List the models this API key can use, to confirm the exact Opus 5 id before running.

  python -m harness.models
"""

from harness.run import make_client

if __name__ == "__main__":
    for m in make_client().models.list(limit=100):
        print(f"{m.id:<32} {getattr(m, 'display_name', '')}")
