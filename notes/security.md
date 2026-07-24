# XSS & CSRF

## 1. XSS (Cross-Site Scripting) Analysis
* **Фронтенд:** Vue 3 экранирует весь вывод в `{{ }}` по умолчанию.
* **Аудит кода:** Выполнена проверка директивы `v-html`. В проекте отсутствует непреднамеренный рендеринг сырого HTML без предварительной очистки (`DOMPurify`).
* **CSP Header:** На бэкенде настроен заголовок Content-Security-Policy для защиты от выполнения сторонних скриптов:
  `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';`

## 2. CSRF (Cross-Site Request Forgery) Protection
* **Механизм аутентификации:** Используются JWT-токены, передаваемые через заголовок `Authorization: Bearer <token>`.
* **Защита от CSRF:** Браузер не передает заголовок `Authorization` автоматически при кросс-доменных запросах (в отличие от Cookies). В сочетании с политикой CORS это делает приложение устойчивым к CSRF-атакам по определению.

## 3. Результаты PoC тестов
- [x] **XSS PoC:** Пейлоуд `<img src=x onerror=alert(1)>` отрендерился как безопасный текст.
- [x] **CSP Test:** Заголовок `Content-Security-Policy` присутствует в ответах API.
- [x] **CSRF Test:** Кросс-доменные запросы без заголовка `Authorization` отклоняются сервером со статусом `401 Unauthorized`.