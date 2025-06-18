# Project TODO List

Here is a list of the remaining issues to be addressed to get the full stack running correctly.

### 1. Prometheus Metrics Configuration
- **Problem**: The `prometheus.yml` is configured to scrape `/metrics` from all custom services (`sandbox`, `time-client`, etc.), but these services do not expose metrics on that endpoint, leading to `404 Not Found` errors.
- **Solution**: We need to either add a Prometheus metrics exporter to each FastAPI application or remove the scrape targets from the `prometheus.yml` file.

### 2. Grafana Dashboard Provisioning
- **Problem**: Grafana is logging warnings about duplicate UIDs, duplicate titles, and restricted database access, which prevents the system overview dashboard from loading.
- **Solution**: The `monitoring/grafana/dashboards/mcp-system-overview.json` file needs to be reviewed and corrected to ensure it has a unique UID and title and is configured correctly for provisioning.

### ~~3. MCPO Service Configuration~~
- **~~Problem~~**: ~~The `mcpo-config.json` file incorrectly points to the `/mcp/sse` endpoint on the backend services. The correct endpoint provided by the `fastapi-mcp` library is `/mcp`. This is causing `mcpo` to fail on startup.~~
- **~~Solution~~**: ~~Update the `mcpo-config.json` file to change all `url` entries from `.../mcp/sse` to `.../mcp`. This is the most critical issue to fix.~~ **DONE** 