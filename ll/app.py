import asyncio
from signal import SIGHUP, SIGINT, SIGTERM
from typing import MutableMapping

import structlog

logger = structlog.get_logger(__name__)


class Application(MutableMapping):
    signals = (SIGHUP, SIGTERM, SIGINT)

    def __init__(self, loop=None):
        self._state = {}
        self._frozen = False

        if loop is None:
            loop = asyncio.get_event_loop()

        self.loop = loop

        self.on_startup = []
        self.on_shutdown = []

        self._setup_signals()

    def __eq__(self, other):
        return self is other

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._check_frozen()
        self._state[key] = value

    def __delitem__(self, key):
        self._check_frozen()
        del self._state[key]

    def __len__(self):
        return len(self._state)

    def __iter__(self):
        return iter(self._state)

    def _check_frozen(self):
        if self._frozen:
            raise RuntimeError(
                "Changing state of started or joined application is forbidden"
            )

    @property
    def frozen(self):
        return self._frozen

    def freeze(self):
        if self._frozen:
            return
        self._frozen = True

    def _setup_signals(self):
        for signal in Application.signals:
            self.loop.add_signal_handler(
                signal, lambda: asyncio.create_task(self.shutdown())
            )

    async def shutdown(self):
        for handler in self.on_shutdown:
            await handler(self)

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

        self.loop.stop()

    def run(self):
        logger.info("==== Running App ====")

        for handler in self.on_startup:
            self.loop.run_until_complete(handler(self))

        self.freeze()

        try:
            self.loop.run_forever()
        finally:
            self.loop.close()
