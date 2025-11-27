import kagglehub
import shutil
import os
from src.config import DATA_PATH

def download_data():
    """Pobieranie zestawu danych z Kaggle i przenoszenie go do skonfigurowanej ścieżki."""
    if os.path.exists(DATA_PATH):
        print(f"Dane już istnieją w {DATA_PATH}")
        return

    print("Pobieranie zestawu danych...")
    try:
        path = kagglehub.dataset_download("blastchar/telco-customer-churn")
        print("Ścieżka pobierania:", path)

        # Znalezienie pliku CSV
        csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
        if not csv_files:
            raise FileNotFoundError("Nie znaleziono pliku CSV w pobranym zbiorze danych.")
        
        csv_file_name = csv_files[0]
        source_file = os.path.join(path, csv_file_name)
        
        # Upewnienie się, że katalog istnieje
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        
        # Przeniesienie i zmiana nazwy
        shutil.copy(source_file, DATA_PATH)
        print(f"SUKCES! Plik skopiowany do: {DATA_PATH}")
        
    except Exception as e:
        print(f"Błąd podczas pobierania danych: {e}")
        raise

if __name__ == "__main__":
    download_data()
