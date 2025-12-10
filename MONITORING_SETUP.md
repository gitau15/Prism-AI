# Monitoring Setup Guide for Prism AI

## Overview

This guide explains how to set up the monitoring and alerting infrastructure for Prism AI. The system includes:

1. Prometheus for metrics collection
2. Grafana for visualization
3. Sentry for error tracking
4. Custom health check endpoints
5. Application-level metrics

## Prerequisites

- Docker and Docker Compose installed
- Python 3.9+ with required dependencies
- Access to a Sentry account (for error tracking)

## Components

### 1. Application-Level Monitoring

The Prism AI application includes built-in monitoring capabilities:

#### Health Check Endpoints

- `/health` - Basic application health
- `/health/db` - Database connectivity health
- `/metrics` - Prometheus metrics endpoint

#### Custom Metrics

The application exposes the following custom metrics:

- `prism_ai_requests_total` - Counter for total HTTP requests
- `prism_ai_request_duration_seconds` - Histogram for request durations

### 2. Prometheus Setup

#### Configuration

The Prometheus configuration is located at `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prism-ai'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

#### Running Prometheus

To run Prometheus with Docker:

```bash
docker run -p 9090:9090 \
  -v ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### 3. Grafana Setup

#### Running Grafana

To run Grafana with Docker:

```bash
docker run -d -p 3000:3000 grafana/grafana
```

#### Dashboard Configuration

Import the dashboard from `monitoring/grafana-dashboard.json`:

1. Access Grafana at http://localhost:3000
2. Log in with default credentials (admin/admin)
3. Go to "Create" → "Import"
4. Upload the `grafana-dashboard.json` file
5. Select Prometheus as the data source

### 4. Sentry Setup

#### Configuration

Sentry is configured in `app/main.py`:

```python
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN_HERE",
    integrations=[
        FastApiIntegration(),
        StarletteIntegration(),
    ],
    traces_sample_rate=1.0,
)
```

Replace `YOUR_SENTRY_DSN_HERE` with your actual Sentry DSN.

#### Features

- Automatic error capturing
- Performance tracing
- User feedback collection
- Release tracking

## Docker Compose Setup

For a complete monitoring stack, use the following `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
```

## Alerting Rules

Create alerting rules in `monitoring/alerting-rules.yml`:

```yaml
groups:
- name: prism-ai-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(prism_ai_requests_total{status=~"5.."}[5m]) > 0.05
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is above 5% for more than 2 minutes"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(prism_ai_request_duration_seconds_bucket[5m])) > 2
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected"
      description: "95th percentile latency is above 2 seconds for more than 2 minutes"
```

## Testing the Monitoring Setup

### 1. Verify Health Endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/db
curl http://localhost:8000/metrics
```

### 2. Generate Traffic

Use a tool like `hey` to generate traffic:

```bash
# Install hey first
go install github.com/rakyll/hey@latest

# Generate traffic
hey -z 30s -c 10 http://localhost:8000/
```

### 3. Check Metrics in Prometheus

1. Access Prometheus at http://localhost:9090
2. Query for `prism_ai_requests_total`
3. Verify metrics are being collected

### 4. View Dashboards in Grafana

1. Access Grafana at http://localhost:3000
2. Navigate to the Prism AI dashboard
3. Verify data is being displayed

## Troubleshooting

### Common Issues

#### Metrics Not Appearing

1. Check that the application is running on the correct port
2. Verify Prometheus is scraping the metrics endpoint
3. Check firewall settings

#### Sentry Not Capturing Errors

1. Verify the DSN is correctly configured
2. Check network connectivity to Sentry
3. Ensure Sentry SDK is properly initialized

#### Grafana Dashboard Issues

1. Verify Prometheus data source is correctly configured
2. Check that metrics exist in Prometheus
3. Validate dashboard JSON format

### Logs and Debugging

Check application logs for monitoring-related messages:

```bash
docker logs prism-ai-app
```

Check Prometheus logs:

```bash
docker logs prometheus
```

## Best Practices

### Metric Design

1. Use consistent naming conventions
2. Include relevant labels for filtering
3. Avoid high-cardinality labels
4. Use appropriate metric types (counter, gauge, histogram)

### Alerting

1. Set appropriate thresholds based on historical data
2. Include meaningful annotations in alerts
3. Use alert grouping to reduce noise
4. Regularly review and tune alerts

### Performance

1. Monitor the monitoring system itself
2. Set resource limits for monitoring components
3. Use sampling for high-volume metrics
4. Regularly clean up old data

## Maintenance

### Regular Tasks

1. Update monitoring configurations as needed
2. Review and tune alert thresholds
3. Monitor resource usage of monitoring components
4. Rotate logs and metrics data

### Upgrades

1. Backup configurations before upgrading
2. Test upgrades in staging environment first
3. Monitor for issues after upgrades
4. Update documentation as needed

## Conclusion

This monitoring setup provides comprehensive observability for Prism AI, allowing you to track performance, detect issues, and maintain system reliability. Regular maintenance and tuning will ensure the monitoring system continues to provide value as the application grows.