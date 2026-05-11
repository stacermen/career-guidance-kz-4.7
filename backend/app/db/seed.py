"""Console entrypoint for seeding (`python -m app.db.seed`)."""

import asyncio

from app.db.seed_data import main

if __name__ == "__main__":
    asyncio.run(main())
