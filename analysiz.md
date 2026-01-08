# Full Codebase Scan, Smell Detection, and Analysis Report

## Definition of Code Smells

A code smell is a surface-level indicator of deeper design, maintainability, readability, or reliability problems within a codebase. They are not necessarily bugs—the code may still function as intended—but they signal technical debt and increased risk of future failures.

Key characteristics of code smells include:
* **Structural Weakness**: Poorly organized code that makes it difficult to add new features or modify existing ones.
* **Unclear Intent**: Code that is hard to read or reason about, often requiring excessive comments or reverse-engineering to understand.
* **Fragile Logic**: Code that is prone to breaking when unrelated parts of the system change.
* **Maintenance Burden**: Patterns that require repetitive changes in multiple places (DRY violations).

---

## Executive Summary

The Anikii API codebase is a FastAPI-based application for scraping and serving anime metadata. While the project is functional and well-structured in terms of route/service separation, it suffers from several critical architectural issues:
1. **Blocking Synchronous I/O**: Extensive use of synchronous database and file drivers in an asynchronous framework.
2. **Resource Management**: Inefficient handling of HTTP client sessions.
3. **Duplicate Logic**: Highly repetitive patterns in services and scrapers.
4. **Hardcoded Secrets**: Sensitive keys and URLs embedded directly in source code.

---

## Status Update (2026-01-07)

- **Issue 1 (Blocking I/O)**: FIXED. Replaced `pymongo` with `motor`, `open()` with `aiofiles`, and `requests` with `httpx.AsyncClient`.
- **Issue 2 (HTTP Client)**: FIXED. Centralized `httpx.AsyncClient` in `fetchHelpers.py` with FastAPI lifespan management in `main.py`.
- **Issue 4 (Hardcoded Secrets)**: FIXED. Moved AES keys, IVs, and API URLs to `config.py` using `pydantic-settings`.
- **Issue 6 & 7 (Logging & DI)**: FIXED. Standardized logging with `logger.py` and introduced lifespan-based resource management.
- **Issue 3 & 5 (Duplication & Lazy Imports)**: IMPROVED. Refactored several services and eliminated lazy imports in database helpers.

## Detailed Findings: Code Smells & Bugs (Archived/Resolved)
... (original content below) ...

### 1. Blocking Synchronous Operations in Async Context
* **File Path**: [get.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/database/get.py#L1-L24), [home.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/routes/home.py#L15)
* **Type**: Bug / Performance Risk
* **Description**: The application uses `pymongo` (a synchronous MongoDB driver) and synchronous `open()` calls within `async` route handlers and services.
* **Impact**: Synchronous calls block the FastAPI event loop. If a database query or file read takes time, the entire API becomes unresponsive to other concurrent requests, negating the benefits of using an asynchronous framework.
* **Recommended Fix**: 
    * Replace `pymongo` with `motor` (the asynchronous MongoDB driver for Python).
    * Use `aiofiles` for asynchronous file I/O.

### 2. Inefficient HTTP Client Management
* **File Path**: [stream_scraper.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/helpers/scrapers/stream_scraper.py#L26), [gogo_episodes.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/helpers/gogo_episodes.py#L16)
* **Type**: Code Smell / Performance Risk
* **Description**: Multiple scrapers and helpers instantiate a new `httpx.AsyncClient()` for every single request or function call.
* **Impact**: Creating a new client for every request is expensive. It prevents connection pooling, leading to high latency and potential socket exhaustion under load.
* **Recommended Fix**: Use a single, shared `httpx.AsyncClient` instance managed via FastAPI's startup/shutdown events (as partially attempted in `fetchHelpers.py`).

### 3. High Degree of Logic Duplication (DRY Violation)
* **File Path**: [anilist_media_service.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/services/anilist_media_service.py), [anilist_discovery_service.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/services/anilist_discovery_service.py)
* **Type**: Code Smell
* **Description**: Every service function follows the exact same pattern: fetch query -> prepare body -> call `make_api_request_async` -> check errors -> return data.
* **Impact**: Increased maintenance effort. A change in error handling or request logic requires updates in dozens of functions across multiple files.
* **Recommended Fix**: Create a generic base service or a helper function that encapsulates the repetitive fetch-and-validate logic.

### 4. Hardcoded Secrets and Sensitive Configuration
* **File Path**: [extractors.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/helpers/extractors.py#L7-L11), [home.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/routes/home.py#L61)
* **Type**: Security Risk / Code Smell
* **Description**: AES keys, IVs, and production URLs (Render links) are hardcoded in the source files.
* **Impact**: Security vulnerability. If these keys are sensitive, they are exposed in the repository. Hardcoded URLs make it difficult to manage different environments (staging vs. production).
* **Recommended Fix**: Move all keys, IVs, and environment-specific URLs to the `Settings` class in `app/core/config.py` and load them via environment variables.

### 5. Mixed Responsibilities & Lazy Imports
* **File Path**: [cacheData.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/helpers/json/cacheData.py#L62)
* **Type**: Code Smell
* **Description**: `cacheData.py` handles both file-based and database-based caching, leading to complex conditional logic. It also uses "lazy imports" inside functions to avoid circular dependencies.
* **Impact**: Violates the Single Responsibility Principle. The code is harder to test and reason about. Lazy imports are often a sign of poor architectural layering.
* **Recommended Fix**: Split the caching logic into dedicated `FileCache` and `DbCache` providers. Refactor module dependencies to eliminate the need for lazy imports.

### 6. Inconsistent Logging and Error Handling
* **File Path**: [gogo_episodes.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/helpers/gogo_episodes.py#L19), [crypto_utils.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/helpers/scrapers/crypto_utils.py#L19)
* **Type**: Code Smell / Maintainability
* **Description**: The codebase mixes `print()` statements with a proper `logger`. Some functions fail silently by returning empty lists or dictionaries without logging the root cause.
* **Impact**: Makes debugging in production environments extremely difficult. `print` statements are often lost or not captured by log aggregators.
* **Recommended Fix**: Standardize on the `app.core.logger`. Ensure all `except` blocks log the exception at an appropriate level (error/warning) before returning fallback values.

### 7. Global State and Singleton Patterns
* **File Path**: [config.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/core/config.py#L46), [get.py](file:///c:/Users/Asterixh/Desktop/my%20tools/Anikii/anikii-be/api.anikii/app/database/get.py#L5)
* **Type**: Code Smell
* **Description**: Heavy reliance on global variables (`_settings`, `_client`, `_async_client`) and singleton getter functions.
* **Impact**: Makes unit testing difficult as state persists between tests. It also makes it harder to implement dependency injection, which is a core feature of FastAPI.
* **Recommended Fix**: Utilize FastAPI's dependency injection system (`Depends`) to provide settings and database sessions to routes and services.

---

## Conclusion

The codebase is functional but requires significant refactoring to be truly production-ready and scalable. Addressing the **Blocking Synchronous I/O** and **HTTP Client Management** should be the highest priority to ensure application stability and performance. Standardization of logging and error handling will greatly improve the developer experience and maintainability of the project.
