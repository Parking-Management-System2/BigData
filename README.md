# Telco Customer Churn Prediction System

## Opis Projektu
System czasu rzeczywistego do przewidywania odejść klientów (churn) w branży telekomunikacyjnej. Projekt demonstruje nowoczesne podejście do Big Data, wykorzystując przetwarzanie strumieniowe, uczenie maszynowe oraz konteneryzację.

System automatycznie:
1.  Pobiera i przetwarza dane historyczne.
2.  Trenuje model Machine Learning (Random Forest).
3.  Symuluje strumień danych klientów w czasie rzeczywistym.
4.  Dokonuje predykcji w locie (Streaming).
5.  Udostępnia wyniki i statystyki przez REST API.

## Instrukcja Uruchomienia

### Wymagania
*   Docker
*   Docker Compose

### Kroki
1.  **Sklonuj repozytorium** (jeśli jeszcze tego nie zrobiłeś).
2.  **Uruchom system**:
    W katalogu głównym projektu wykonaj komendę:
    ```bash
    docker compose up -d --build
    ```
    *Flaga `--build` jest zalecana przy pierwszym uruchomieniu lub po zmianach w kodzie.*

3.  **Dostęp do API**:
    Po kilku chwilach (potrzebnych na start kontenerów i trening modelu) API będzie dostępne pod adresem:
    [http://localhost:8000](http://localhost:8000)

    *   Dokumentacja Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
    *   Sprawdzenie statusu: [http://localhost:8000/](http://localhost:8000/)

## Komponenty Systemu

### 1. Kafka & Zookeeper
Fundament komunikacji w systemie.
*   **Zookeeper**: Zarządza klastrem Kafki.
*   **Kafka**: Szyna danych. Przechowuje strumień zdarzeń o klientach w temacie `telco-churn`. Gwarantuje niezawodność i buforowanie danych między producentem a konsumentem.

### 2. Producer (`src/producer.py`)
Symulator rzeczywistego ruchu.
*   Wczytuje historyczny zbiór danych.
*   Losuje próbki klientów.
*   Wysyła je cyklicznie do Kafki, symulując napływ nowych danych do systemu.

### 3. Spark Worker (`src/consumer.py` & `src/model.py`)
Główny silnik analityczny.
*   **Trening Modelu**: Przy starcie sprawdza, czy istnieje wytrenowany model. Jeśli nie, pobiera dane, przetwarza je (pipeline: StringIndexer, VectorAssembler) i trenuje klasyfikator Random Forest.
*   **Przetwarzanie Strumieniowe**: Uruchamia Spark Structured Streaming, który nasłuchuje na temacie Kafki.
*   **Predykcja**: Dla każdej otrzymanej wiadomości wykonuje predykcję (Churn: Tak/Nie) i oblicza prawdopodobieństwo.
*   **Zapis**: Wyniki są zapisywane w czasie rzeczywistym do bazy PostgreSQL.

### 4. PostgreSQL
Relacyjna baza danych.
*   Przechowuje historię wszystkich predykcji w tabeli `churn_predictions`.
*   Umożliwia backendowi szybkie agregowanie danych i generowanie statystyk historycznych.

### 5. Backend API (`backend/main.py`)
Interfejs dla użytkownika i aplikacji frontendowych. Zbudowany w oparciu o **FastAPI**.
*   **Endpointy**:
    *   `/` - Healthcheck (sprawdza połączenie z bazą).
    *   `/stats` - Ogólne statystyki (liczba predykcji, wskaźnik odejść).
    *   `/recent` - Lista ostatnich predykcji.
    *   `/predictions/{customer_id}` - Historia predykcji dla konkretnego klienta.
    *   `/risk-distribution` - Rozkład ryzyka odejścia.
    *   `/churn-over-time` - Wykres odejść w czasie.
    *   `/submit` - Ręczne przesyłanie danych klienta do analizy.
