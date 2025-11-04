# Test Examples: How Tests Catch Configuration Issues

This document demonstrates how the test suite catches common configuration mistakes.

## Example 1: Missing Dashboard UID

**Broken Configuration:**
```json
{
  "id": null,
  "title": "Internet Speed Monitor",
  ...
}
```

**Test That Catches It:**
```
tests/test_grafana_config.py::TestDashboardConfiguration::test_dashboard_has_uid_field FAILED

AssertionError: Dashboard must have a 'uid' field
```

**Impact:** Without UID, dashboard URL changes randomly, breaking bookmarks and links.

---

## Example 2: Invalid UID Format

**Broken Configuration:**
```json
{
  "uid": "speed monitor dashboard!",
  ...
}
```

**Test That Catches It:**
```
tests/test_grafana_config.py::TestDashboardConfiguration::test_dashboard_uid_format FAILED

AssertionError: Dashboard UID 'speed monitor dashboard!' contains invalid characters.
Must be alphanumeric with hyphens or underscores only.
```

**Impact:** Grafana may reject the dashboard or generate invalid URLs.

---

## Example 3: Hard-coded Token

**Broken Configuration:**
```yaml
secureJsonData:
  token: abc123xyz789hardcodedtoken
```

**Test That Catches It:**
```
tests/test_grafana_config.py::TestDatasourceConfiguration::test_datasource_uses_environment_variable FAILED

AssertionError: Datasource should use ${INFLUXDB_TOKEN} environment variable syntax
```

**Impact:** Security vulnerability - token exposed in version control, not configurable.

---

## Example 4: Token in Wrong Section

**Broken Configuration:**
```yaml
jsonData:
  version: Flux
  organization: speedmonitor
  token: ${INFLUXDB_TOKEN}  # Wrong section!
```

**Test That Catches It:**
```
tests/test_grafana_config.py::TestConfigurationSecurity::test_datasource_token_not_in_jsondata FAILED

AssertionError: Token should not be in jsonData section (security risk).
Use secureJsonData instead.
```

**Impact:** Token exposed via Grafana API, security vulnerability.

---

## Example 5: Mismatched Datasource UID

**Broken Dashboard Configuration:**
```json
{
  "targets": [{
    "datasource": {
      "uid": "wrong-datasource-uid"
    }
  }]
}
```

**Test That Catches It:**
```
tests/test_grafana_config.py::TestDashboardConfiguration::test_dashboard_panels_reference_correct_datasource FAILED

AssertionError: Panel 1 references datasource 'wrong-datasource-uid',
expected 'influxdb-datasource'
```

**Impact:** Dashboard panels won't load data, showing "datasource not found" errors.

---

## Example 6: Mismatched Bucket Names

**Broken Datasource:**
```yaml
jsonData:
  defaultBucket: wrongbucket
```

**Dashboard Query:**
```
from(bucket: "speedtest")
```

**Test That Catches It:**
```
tests/test_grafana_config.py::TestConfigurationIntegration::test_bucket_names_consistent FAILED

AssertionError: Panel 1 queries bucket 'speedtest',
but datasource default bucket is 'wrongbucket'
```

**Impact:** Queries may fail or return no data due to bucket mismatch.

---

## Example 7: Invalid JSON

**Broken Configuration:**
```json
{
  "uid": "speedmonitor-dashboard",
  "title": "Internet Speed Monitor"
  "tags": ["speedtest"]  // Missing comma
}
```

**Test That Catches It:**
```
tests/test_grafana_config.py::TestDashboardConfiguration::test_dashboard_is_valid_json FAILED

Dashboard JSON is invalid: Expecting ',' delimiter: line 4 column 3 (char 89)
```

**Impact:** Grafana can't load the dashboard at all.

---

## Example 8: Missing Required Fields

**Broken Datasource:**
```yaml
datasources:
  - name: InfluxDB
    type: influxdb
    # Missing: url, uid, organization
```

**Test That Catches It:**
```
tests/test_grafana_config.py::TestDatasourceConfiguration::test_datasource_configuration_structure FAILED

AssertionError: Datasource configuration should have 'url:' field
```

**Impact:** Datasource can't connect to InfluxDB, dashboard shows no data.

---

## Example 9: Wrong Environment Variable Format

**Broken Configuration:**
```yaml
secureJsonData:
  token: $INFLUXDB_TOKEN  # Missing curly braces
```

**Test That Catches It:**
```
tests/test_grafana_config.py::TestConfigurationIntegration::test_environment_variable_format FAILED

AssertionError: Found invalid environment variable format: ['$INFLUXDB_TOKEN'].
Use ${VAR_NAME} format.
```

**Impact:** Grafana may not expand the variable, treating it as literal string.

---

## Running Individual Tests

To verify these tests catch issues, you can run them individually:

```bash
# Test dashboard UID presence
uv run pytest tests/test_grafana_config.py::TestDashboardConfiguration::test_dashboard_has_uid_field -v

# Test for hard-coded tokens
uv run pytest tests/test_grafana_config.py::TestDatasourceConfiguration::test_datasource_no_hardcoded_tokens -v

# Test datasource/dashboard UID consistency
uv run pytest tests/test_grafana_config.py::TestConfigurationIntegration::test_datasource_uid_matches_dashboard_references -v

# Test security
uv run pytest tests/test_grafana_config.py::TestConfigurationSecurity -v
```

## Test-Driven Configuration Workflow

1. **Make configuration change**
2. **Run tests:** `uv run pytest tests/test_grafana_config.py -v`
3. **Fix any failures** indicated by test output
4. **Verify all tests pass** before committing
5. **Commit with confidence** knowing configuration is valid

## Benefits

- **Catch mistakes early:** Before deployment/runtime
- **Clear error messages:** Tests tell you exactly what's wrong
- **Regression prevention:** Tests ensure future changes don't break existing config
- **Documentation:** Tests serve as specification for correct configuration
- **CI/CD ready:** Automated validation on every commit

---

**Note:** All examples above are hypothetical demonstrations. The actual configuration files currently pass all tests successfully.
