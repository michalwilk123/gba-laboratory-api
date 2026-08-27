# GBA Laboratory API

REST API do obsługi próbek laboratoryjnych, wyników badań oraz przygotowania danych do
eksportu integracyjnego. Eksport zawiera wyłącznie zatwierdzone wyniki.

## Zakres aplikacji

- rejestrowanie, listowanie i pobieranie próbek,
- zmiana statusu próbki,
- dodawanie i listowanie wyników,
- zatwierdzanie wyników,
- filtrowanie i paginacja list,
- eksport próbki z zatwierdzonymi wynikami,
- uwierzytelnianie JWT,
- dokumentacja OpenAPI, Swagger UI i ReDoc,
- przykładowe dane oraz testy API.

## Pytania do uzupełnienia przed oddaniem zadania

Poniższe pytania są celowo pozostawione bez odpowiedzi.

#### 1. Dlaczego wybrałeś ten framework i taką strukturę aplikacji?

Aplikacja według wymagań przypomina najbardziej aplikacje typu CRUD opartą o baze danych. Tego typu aplikacje łatwiej jest zbudować w Django niż w FastAPI.
Póki co jest mało kodu i aplikacja jest prosta i czytelna i jest wszystko co jest potrzebne


#### 2. Jak zaprojektowałeś model danych?

Model składa się z dwóch głównych encji: próbki i wyniku. Próbka może mieć wiele wyników, ale tylko jeden dla danego parametru. sample_id jest unikalnym identyfikatorem biznesowym, a UUID służy jako identyfikator techniczny. Usunięcie próbki z istniejącymi wynikami jest blokowane, żeby zachować spójność danych.


#### 3. Jak zaprojektowałeś obsługę statusów próbek i wyników?

Statusy zostały zaimplementowane jako jawne zestawy wartości przy użyciu TextChoices w modelach Django. Próbka może mieć status registered, in_progress, completed lub cancelled, a wynik draft lub approved. Poprawność wartości jest sprawdzana przez serializery. Obsługa statusów została celowo uproszczona do wymagań zadania.


#### 4. Jak rozwiązanie można rozwinąć pod integrację z systemem zewnętrznym, np. ERP, CRM, portalem klienta albo

platformą e-commerce?
Można rozbudować o funkcjonalność webhooków, które będą wysyłać powiadomienia o zmianach stausów do zewnętrznych serwisów.

## Technologie

- Python 3.14.7
- Django 5.2 i Django REST Framework
- PostgreSQL 17
- Django ORM i django-filter
- Simple JWT
- drf-spectacular
- Factory Boy
- Gunicorn
- Docker Compose i uv

## Wymagania

- Docker z Docker Compose
- opcjonalnie `uv` do uruchamiania lokalnych kontroli jakości kodu

## Konfiguracja

Utwórz lokalny plik środowiskowy:

```bash
cp .env.example .env
```

Przed uruchomieniem zastąp wartości `DJANGO_SECRET_KEY` i `POSTGRES_PASSWORD` w pliku `.env`.
Plik `.env` nie jest śledzony przez Git.

## Uruchomienie

Uruchom bazę danych, zbuduj obraz aplikacji, wykonaj migracje i załaduj przykładowe dane:

```bash
docker compose up -d db
docker compose build api
docker compose run --rm api uv run python manage.py migrate
docker compose run --rm api uv run python manage.py seed_data
```

Utwórz użytkownika API i uruchom aplikację:

```bash
docker compose run --rm api uv run python manage.py createsuperuser
docker compose up -d api
```

Aplikacja jest dostępna pod adresem <http://localhost:8000>.

Zatrzymanie usług:

```bash
docker compose down
```

## Dokumentacja i uwierzytelnianie

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- schemat OpenAPI: <http://localhost:8000/schema>

Tokeny JWT można uzyskać przez `POST /auth/token`, przekazując nazwę i hasło utworzonego
użytkownika. Token dostępu należy wysyłać w nagłówku:

```text
Authorization: Bearer <access_token>
```

W Swagger UI token można ustawić przyciskiem **Authorize**.

## Przykładowe dane

Polecenie `seed_data` jest idempotentne i tworzy:

- próbkę `SMP-001` ze statusem `completed`,
- zatwierdzony wynik `Protein = 12.5%`,
- roboczy wynik `Moisture = 8.75%`.

Ponowne wykonanie polecenia nie duplikuje danych:

```bash
docker compose run --rm api uv run python manage.py seed_data
```

## Testy

Testy korzystają z PostgreSQL uruchomionego przez Docker Compose:

```bash
docker compose up -d db
docker compose run --rm api uv run python manage.py test --noinput
```

Kontrola lintowania i formatowania:

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run ruff format --check .
```

## Endpointy API

Endpointy nie mają końcowego ukośnika.

| Metoda | Endpoint | Opis |
| --- | --- | --- |
| `POST` | `/samples` | Dodanie próbki |
| `GET` | `/samples` | Lista próbek |
| `GET` | `/samples/{sample_id}` | Szczegóły próbki po identyfikatorze biznesowym |
| `PATCH` | `/samples/{sample_id}/status` | Zmiana statusu próbki |
| `GET` | `/samples/{sample_id}/results` | Wyniki przypisane do próbki |
| `POST` | `/results` | Dodanie wyniku |
| `GET` | `/results` | Lista wyników |
| `PATCH` | `/results/{result_id}/approve` | Zatwierdzenie wyniku |
| `GET` | `/integration/export/{sample_id}` | Eksport próbki i zatwierdzonych wyników |
| `POST` | `/auth/token` | Uzyskanie pary tokenów JWT |
| `POST` | `/auth/token/refresh` | Odświeżenie tokenu dostępu |

Listy próbek i wyników obsługują paginację. Dostępne filtry są widoczne w dokumentacji
OpenAPI.
