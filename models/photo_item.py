import os


class PhotoItem:
    """Merepresentasikan satu objek foto dengan atribut terenkapsulasi (OOP 1)."""

    def __init__(self, file_path: str):
        # Atribut privat menggunakan double underscore (__)
        self.__filename = os.path.basename(file_path)
        self.__source_path = file_path
        self.__current_path = file_path
        self.__score = 0.0
        self.__detail = "-"
        self.__status = "Pending"

    # --- Getter ---
    def get_filename(self) -> str:
        return self.__filename

    def get_source_path(self) -> str:
        return self.__source_path

    def get_current_path(self) -> str:
        return self.__current_path

    def get_score(self) -> float:
        return self.__score

    def get_detail(self) -> str:
        return self.__detail

    def get_status(self) -> str:
        return self.__status

    # --- Setter ---
    def set_analysis_result(self, score: float, status: str, detail: str):
        self.__score = score
        self.__status = status
        self.__detail = detail

    def set_current_path(self, new_path: str):
        self.__current_path = new_path