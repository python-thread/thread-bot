import asyncio
from src import main

if __name__ == '__main__':
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    pass
  except Exception as e:
    raise RuntimeError('Failed to start') from e
