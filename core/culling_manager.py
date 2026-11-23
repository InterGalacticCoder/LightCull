import os
import shutil
from models.photo_item import PhotoItem
from models.data_structures import PhotoQueue, UndoStack
from core.analyzer import ExposureAnalyzer, AutoGrayscaleAnalyzer


class CullingManager:
    """Mengelola antrean foto (Queue), riwayat undo (Stack), dan pemindahan file."""

    VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

    def __init__(self):
        self.__queue = PhotoQueue()
        self.__undo_stack = UndoStack()
        self.__analyzer: ExposureAnalyzer = AutoGrayscaleAnalyzer()
        self.__source_folder = ""
        self.__stats = {
            "Total": 0,
            "Normal": 0,
            "Underexposed": 0,
            "Overexposed": 0,
        }

    def set_analyzer(self, analyzer: ExposureAnalyzer):
        """Polymorphism: mengganti strategi analisis tanpa mengubah logika culling."""
        self.__analyzer = analyzer

    def set_source_folder(self, folder_path: str):
        self.__source_folder = folder_path
        self.__queue.clear()
        self.__undo_stack.clear()
        self.__stats = {
            "Total": 0,
            "Normal": 0,
            "Underexposed": 0,
            "Overexposed": 0,
        }

    def get_source_folder(self) -> str:
        return self.__source_folder

    def load_folder_to_queue(self) -> int:
        """Memindai file foto di folder sumber lalu memasukkannya ke Queue (FIFO)."""
        self.__queue.clear()
        if not self.__source_folder or not os.path.isdir(self.__source_folder):
            return 0

        for filename in sorted(os.listdir(self.__source_folder)):
            full_path = os.path.join(self.__source_folder, filename)
            if os.path.isfile(full_path) and filename.lower().endswith(self.VALID_EXTENSIONS):
                photo = PhotoItem(full_path)
                self.__queue.enqueue(photo)

        return self.__queue.size()

    def _get_unique_destination(self, dest_folder: str, filename: str) -> str:
        """Mencegah file tertimpa jika nama file sudah ada di subfolder tujuan."""
        base, ext = os.path.splitext(filename)
        dest_path = os.path.join(dest_folder, filename)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_folder, f"{base}_{counter}{ext}")
            counter += 1
        return dest_path

    def process_next(self) -> tuple[PhotoItem | None, str | None]:
        """Mengambil 1 foto dari Queue, menganalisis, memindahkan file, dan mencatat ke Stack."""
        if self.__queue.is_empty():
            return None, None

        photo: PhotoItem = self.__queue.dequeue()
        old_path = photo.get_current_path()

        try:
            score, status, detail = self.__analyzer.analyze(old_path)
            photo.set_analysis_result(score, status, detail)

            dest_folder = os.path.join(self.__source_folder, status)
            os.makedirs(dest_folder, exist_ok=True)
            dest_path = self._get_unique_destination(dest_folder, photo.get_filename())

            shutil.move(old_path, dest_path)
            photo.set_current_path(dest_path)

            self.__undo_stack.push({
                "photo": photo,
                "from_path": old_path,
                "to_path": dest_path,
                "status": status,
            })

            self.__stats["Total"] += 1
            self.__stats[status] += 1
            return photo, None

        except Exception as err:
            return photo, str(err)

    def undo_last(self) -> dict | None:
        """Mengembalikan 1 file terakhir yang dipindahkan menggunakan Stack.pop()."""
        if self.__undo_stack.is_empty():
            return None

        record = self.__undo_stack.pop()
        if os.path.exists(record["to_path"]):
            restore_path = self._get_unique_destination(
                os.path.dirname(record["from_path"]),
                os.path.basename(record["from_path"]),
            )
            shutil.move(record["to_path"], restore_path)
            record["photo"].set_current_path(restore_path)

        status = record["status"]
        self.__stats["Total"] = max(0, self.__stats["Total"] - 1)
        self.__stats[status] = max(0, self.__stats[status] - 1)
        return record

    def undo_all(self) -> int:
        """Mengembalikan seluruh foto di Stack menggunakan perulangan while."""
        restored_count = 0
        while not self.__undo_stack.is_empty():
            if self.undo_last() is not None:
                restored_count += 1
        return restored_count

    def get_stats(self) -> dict:
        return self.__stats.copy()

    def get_queue_size(self) -> int:
        return self.__queue.size()

    def get_undo_size(self) -> int:
        return self.__undo_stack.size()

    def is_queue_empty(self) -> bool:
        return self.__queue.is_empty()

    def is_undo_empty(self) -> bool:
        return self.__undo_stack.is_empty()