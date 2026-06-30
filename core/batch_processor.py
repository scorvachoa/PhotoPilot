import os
import time
from dataclasses import dataclass, field
from threading import Thread
from typing import Callable

from PIL import Image

from core.state import AppState
from core.pipeline import ProcessingPipeline
from core.exporter import Exporter


@dataclass
class BatchProgress:
    current: int = 0
    total: int = 0
    errors: int = 0
    elapsed: float = 0.0
    finished: bool = False


class BatchProcessor:
    def __init__(self) -> None:
        self._running = False
        self._progress = BatchProgress()

    def process(self, state: AppState,
                on_progress: Callable[[BatchProgress], None],
                on_complete: Callable[[], None]) -> None:
        if self._running:
            return
        self._progress = BatchProgress()
        self._running = True
        thread = Thread(target=self._run,
                        args=(state, on_progress, on_complete),
                        daemon=True)
        thread.start()

    def _run(self, state: AppState,
             on_progress: Callable[[BatchProgress], None],
             on_complete: Callable[[], None]) -> None:
        start = time.time()
        self._progress.total = len(state.images)
        pipeline = ProcessingPipeline()
        exporter = Exporter(state.export)
        os.makedirs(state.output_dir, exist_ok=True)

        for i, path in enumerate(state.images):
            if not self._running:
                break
            try:
                state.current_index = i
                state.original_image = Image.open(path).convert("RGB")
                result = pipeline.process(state)
                if result:
                    exporter.save(result, path, state.output_dir, i)
                self._progress.current = i + 1
            except Exception:
                self._progress.errors += 1
            self._progress.elapsed = time.time() - start
            on_progress(self._progress)

        self._running = False
        self._progress.finished = True
        self._progress.elapsed = time.time() - start
        on_progress(self._progress)
        on_complete()

    def cancel(self) -> None:
        self._running = False
