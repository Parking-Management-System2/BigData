# Telco Customer Churn Prediction System

## Opis Projektu

System czasu rzeczywistego do przewidywania odejść klientów (churn) w branży telekomunikacyjnej. Projekt demonstruje nowoczesne podejście do Big Data, wykorzystując przetwarzanie strumieniowe, uczenie maszynowe oraz konteneryzację.

System automatycznie:

1.  Pobiera i przetwarza dane historyczne.
2.  Trenuje model Machine Learning (Random Forest).
3.  Symuluje strumień danych klientów w czasie rzeczywistym.
4.  Dokonuje predykcji w locie (Streaming).
5.  Udostępnia wyniki i statystyki przez REST API.
6.  Prezentuje dane na interaktywnym dashboardzie.

## Instrukcja Uruchomienia

### Wymagania

-   Docker
-   Docker Compose

### Kroki

1.  **Sklonuj repozytorium** (jeśli jeszcze tego nie zrobiłeś).
2.  **Uruchom system**:
    W katalogu głównym projektu wykonaj komendę:

    ```bash
    docker compose up -d --build
    ```

    _Flaga `--build` jest zalecana przy pierwszym uruchomieniu lub po zmianach w kodzie._

3.  **Dostęp do aplikacji**:
    Po kilku chwilach (potrzebnych na start kontenerów i trening modelu):

    -   **Frontend (Dashboard)**: [http://localhost:3000](http://localhost:3000)
    -   **Backend API**: [http://localhost:8000](http://localhost:8000)
    -   **Dokumentacja Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Komponenty Systemu

### 1. Frontend (`frontend/`)

Nowoczesny interfejs użytkownika zbudowany w technologiach:

-   **React 19** z TypeScript
-   **Tailwind CSS 4** - stylowanie
-   **Framer Motion** - animacje
-   **Recharts** - wykresy i wizualizacje
-   **React Router** - nawigacja SPA

**Funkcjonalności**:

-   **Panel główny** - statystyki w czasie rzeczywistym, wykresy trendów odpływu, rozkład ryzyka
-   **Formularz predykcji** - ręczne wprowadzanie danych klienta do analizy
-   **Szczegóły predykcji** - pełna analiza ryzyka dla wybranego klienta z historią

Serwowany przez **Nginx** z konfiguracją proxy do backendu.

### 2. Kafka & Zookeeper

Fundament komunikacji w systemie.

-   **Zookeeper**: Zarządza klastrem Kafki.
-   **Kafka**: Szyna danych. Przechowuje strumień zdarzeń o klientach w temacie `telco-churn`. Gwarantuje niezawodność i buforowanie danych między producentem a konsumentem.

### 3. Producer (`src/producer.py`)

Symulator rzeczywistego ruchu.

-   Wczytuje historyczny zbiór danych.
-   Losuje próbki klientów.
-   Wysyła je cyklicznie do Kafki, symulując napływ nowych danych do systemu.

### 4. Spark Worker (`src/consumer.py` & `src/model.py`)

Główny silnik analityczny.

-   **Trening Modelu**: Przy starcie sprawdza, czy istnieje wytrenowany model. Jeśli nie, pobiera dane, przetwarza je (pipeline: StringIndexer, VectorAssembler) i trenuje klasyfikator Random Forest.
-   **Przetwarzanie Strumieniowe**: Uruchamia Spark Structured Streaming, który nasłuchuje na temacie Kafki.
-   **Predykcja**: Dla każdej otrzymanej wiadomości wykonuje predykcję (Churn: Tak/Nie) i oblicza prawdopodobieństwo.
-   **Zapis**: Wyniki są zapisywane w czasie rzeczywistym do bazy PostgreSQL.

### 5. PostgreSQL

Relacyjna baza danych.

-   Przechowuje historię wszystkich predykcji w tabeli `churn_predictions`.
-   Umożliwia backendowi szybkie agregowanie danych i generowanie statystyk historycznych.

### 6. Backend API (`backend/main.py`)

Interfejs dla użytkownika i aplikacji frontendowych. Zbudowany w oparciu o **FastAPI**.

-   **Endpointy**:
    -   `/` - Healthcheck (sprawdza połączenie z bazą).
    -   `/stats` - Ogólne statystyki (liczba predykcji, wskaźnik odejść).
    -   `/recent` - Lista ostatnich predykcji.
    -   `/predictions/{customer_id}` - Historia predykcji dla konkretnego klienta.
    -   `/risk-distribution` - Rozkład ryzyka odejścia.
    -   `/churn-over-time` - Wykres odejść w czasie.
    -   `/submit` - Ręczne przesyłanie danych klienta do analizy.
