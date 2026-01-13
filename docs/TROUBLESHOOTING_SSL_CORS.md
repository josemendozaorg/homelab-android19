# Troubleshooting Guide: SSL & CORS in Coolify

This guide provides solutions for recurring infrastructure issues in the `homelab-android19` environment, specifically when using Coolify behind Cloudflare.

## 1. SSL Certificate Deadlock (HTTP-01 vs Cloudflare Proxy)

### Symptom
New subdomains fail to load, showing `504 Gateway Timeout` or `ERR_SSL_PROTOCOL_ERROR`. Coolify Proxy logs show ACME `403` or `429` errors.

### Why it happens
HTTP-01 challenges require port 80 to be clear. Cloudflare Proxy (Orange Cloud) forces HTTPS redirection. If the server doesn't have a cert yet, Cloudflare can't connect, and validation fails.

### Solution: DNS-01 Challenge
Configure the Traefik proxy to use DNS validation via Cloudflare API.

1.  **Generate Token**: In Cloudflare, create an API Token with `Zone:DNS:Edit` permissions.
2.  **Coolify Proxy Config**:
    *   Add `CF_DNS_API_TOKEN=<token>` to Environment Variables.
    *   Update `command` section in the Proxy configuration:
        ```bash
        --certificatesresolvers.letsencrypt.acme.dnschallenge=true
        --certificatesresolvers.letsencrypt.acme.dnschallenge.provider=cloudflare
        ```
3.  **Wildcards**: This also allows using wildcard certificates (`*.josemendoza.dev`).

---

## 2. Persistent 403 Forbidden (CORS in Nested Proxies)

### Symptom
The application loads (HTML/JS works), but `POST/PUT/DELETE` requests to the API fail with `403 Forbidden`, often with the message `Invalid CORS request`.

### Why it happens
When traffic flows `Cloudflare (HTTPS) -> Traefik (HTTP) -> Nginx (HTTP) -> Backend`, the `Origin` header (`https://...`) doesn't match the internal protocol (`http`), causing Spring Boot or other frameworks to reject the request.

### Solution: Proxy-Side CORS & Spoofing
Do not rely on the Backend to handle CORS. Handle it at the most immediate proxy (Nginx).

1.  **Nginx CORS Preflight**:
    Handle `OPTIONS` requests in Nginx and return `204`.
2.  **Manual Header Injection**:
    Use `add_header ... always;` to ensure headers are present even on 4xx/500 errors.
3.  **Backend Spoofing**:
    Overwrite headers sent to the upstream to make it appear as a Same-Origin local request:
    ```nginx
    proxy_set_header Host "backend:8080";
    proxy_set_header Origin "http://backend:8080";
    ```

---

## 3. General Best Practices
*   **Logs**: If an error isn't appearing in the Nginx logs, it's being blocked by **Cloudflare WAF**. Toggle the record to "DNS Only" (Gray Cloud) to confirm.
*   **Database**: Always use Flyway or Liquibase for seed data required by the Frontend (e.g., test users, category constants).
