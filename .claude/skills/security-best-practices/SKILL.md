---
name: security-best-practices
description: Implement Snowflake security best practices. Use when configuring RBAC, network policies, data masking, row access policies, encryption, audit logging, or secure data sharing. Covers Snowflake-specific security features and OWASP-aligned data protection.
metadata:
  tags: security, Snowflake, RBAC, network-policy, data-masking, row-access-policy, encryption, audit
---

# Snowflake Security Best Practices

## When to use this skill

- **New project**: Set up RBAC and security policies from the start
- **Security audit**: Review and harden Snowflake security posture
- **Data governance**: Implement masking, tagging, and access policies
- **Compliance**: GDPR, HIPAA, SOC2, PCI-DSS alignment

## Instructions

### Step 1: Role-Based Access Control (RBAC)

Design a role hierarchy following the principle of least privilege.

```sql
-- Functional roles (what you CAN do)
CREATE ROLE data_reader;
CREATE ROLE data_writer;
CREATE ROLE data_engineer;
CREATE ROLE data_admin;

-- Role hierarchy
GRANT ROLE data_reader TO ROLE data_writer;
GRANT ROLE data_writer TO ROLE data_engineer;
GRANT ROLE data_engineer TO ROLE data_admin;

-- Database-level grants
GRANT USAGE ON DATABASE my_db TO ROLE data_reader;
GRANT USAGE ON ALL SCHEMAS IN DATABASE my_db TO ROLE data_reader;
GRANT SELECT ON ALL TABLES IN DATABASE my_db TO ROLE data_reader;
GRANT SELECT ON FUTURE TABLES IN DATABASE my_db TO ROLE data_reader;

-- Write access
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA my_db.staging TO ROLE data_writer;
GRANT INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA my_db.staging TO ROLE data_writer;

-- Engineer: full DDL on staging/analytics
GRANT CREATE TABLE, CREATE VIEW, CREATE STAGE, CREATE PIPE, CREATE STREAM, CREATE TASK
    ON SCHEMA my_db.staging TO ROLE data_engineer;
GRANT CREATE TABLE, CREATE VIEW
    ON SCHEMA my_db.analytics TO ROLE data_engineer;

-- Warehouse grants
GRANT USAGE ON WAREHOUSE MOVING_INTEL_WH TO ROLE data_reader;
GRANT OPERATE ON WAREHOUSE MOVING_INTEL_WH TO ROLE data_engineer;

-- Assign roles to users
GRANT ROLE data_reader TO USER analyst_user;
GRANT ROLE data_engineer TO USER etl_user;
```

**Best practices:**
- Never grant privileges directly to users — always through roles
- Use FUTURE GRANTS to auto-apply on new objects
- Separate functional roles (what) from access roles (who)
- Review grants regularly: `SHOW GRANTS TO ROLE <role>;`

### Step 2: Network Policies

Restrict access by IP address.

```sql
-- Allow only office and VPN IPs
CREATE NETWORK POLICY office_only
    ALLOWED_IP_LIST = ('203.0.113.0/24', '198.51.100.0/24')
    BLOCKED_IP_LIST = ('203.0.113.99');

-- Apply to account
ALTER ACCOUNT SET NETWORK_POLICY = office_only;

-- Apply to specific user
ALTER USER service_account SET NETWORK_POLICY = office_only;

-- Verify
SELECT SYSTEM$ALLOWLIST();
```

**Best practices:**
- Always set account-level network policy in production
- Use separate policies for service accounts vs. human users
- Include VPN and CI/CD IP ranges
- Test policy before applying to account level

### Step 3: Dynamic Data Masking

Protect sensitive data with column-level masking policies.

```sql
-- Full masking for non-privileged roles
CREATE MASKING POLICY pii_mask AS (val STRING)
RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('DATA_ADMIN', 'ACCOUNTADMIN') THEN val
        ELSE '***MASKED***'
    END;

-- Email masking (show domain only)
CREATE MASKING POLICY email_mask AS (val STRING)
RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('DATA_ADMIN') THEN val
        WHEN CURRENT_ROLE() IN ('DATA_ENGINEER') THEN
            CONCAT('***@', SPLIT_PART(val, '@', 2))
        ELSE '***MASKED***'
    END;

-- Numeric masking (e.g., salary)
CREATE MASKING POLICY number_mask AS (val NUMBER)
RETURNS NUMBER ->
    CASE
        WHEN CURRENT_ROLE() IN ('DATA_ADMIN') THEN val
        ELSE 0
    END;

-- Apply to columns
ALTER TABLE staging.users MODIFY COLUMN email SET MASKING POLICY email_mask;
ALTER TABLE staging.users MODIFY COLUMN phone SET MASKING POLICY pii_mask;
ALTER TABLE staging.employees MODIFY COLUMN salary SET MASKING POLICY number_mask;
```

### Step 4: Row Access Policies

Control which rows each role can see.

```sql
-- Row access policy: users see only their department's data
CREATE ROW ACCESS POLICY department_policy AS (department_col STRING)
RETURNS BOOLEAN ->
    CURRENT_ROLE() IN ('DATA_ADMIN', 'ACCOUNTADMIN')
    OR department_col = CURRENT_USER()
    OR EXISTS (
        SELECT 1 FROM access_control.department_access
        WHERE role_name = CURRENT_ROLE()
        AND department = department_col
    );

-- Apply to table
ALTER TABLE staging.employees
    ADD ROW ACCESS POLICY department_policy ON (department);
```

### Step 5: Object Tagging and Governance

```sql
-- Create tags for data classification
CREATE TAG pii_level ALLOWED_VALUES 'HIGH', 'MEDIUM', 'LOW', 'NONE';
CREATE TAG data_domain ALLOWED_VALUES 'FINANCE', 'HR', 'MARKETING', 'ENGINEERING';

-- Apply tags
ALTER TABLE staging.users SET TAG pii_level = 'HIGH';
ALTER TABLE staging.users MODIFY COLUMN email SET TAG pii_level = 'HIGH';
ALTER TABLE staging.users MODIFY COLUMN username SET TAG pii_level = 'MEDIUM';

-- Query tagged objects
SELECT * FROM TABLE(
    INFORMATION_SCHEMA.TAG_REFERENCES('staging.users', 'TABLE')
);

-- Find all HIGH PII columns
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS('staging.users', 'TABLE'))
WHERE TAG_NAME = 'PII_LEVEL' AND TAG_VALUE = 'HIGH';
```

### Step 6: Audit and Access History

```sql
-- Query access history (who accessed what)
SELECT
    query_start_time,
    user_name,
    role_name,
    direct_objects_accessed
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE query_start_time > DATEADD('DAY', -7, CURRENT_TIMESTAMP())
ORDER BY query_start_time DESC;

-- Login history (detect suspicious access)
SELECT
    event_timestamp,
    user_name,
    client_ip,
    reported_client_type,
    is_success
FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY
WHERE event_timestamp > DATEADD('DAY', -7, CURRENT_TIMESTAMP())
    AND is_success = 'NO'
ORDER BY event_timestamp DESC;

-- Monitor privilege changes
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
WHERE DELETED_ON IS NULL
ORDER BY CREATED_ON DESC
LIMIT 100;
```

### Step 7: Secure Data Sharing

```sql
-- Create share
CREATE SHARE analytics_share;

-- Grant access to objects
GRANT USAGE ON DATABASE my_db TO SHARE analytics_share;
GRANT USAGE ON SCHEMA my_db.analytics TO SHARE analytics_share;
GRANT SELECT ON TABLE my_db.analytics.daily_metrics TO SHARE analytics_share;

-- Use secure views for row-level filtering
CREATE SECURE VIEW analytics.shared_metrics AS
SELECT * FROM analytics.daily_metrics
WHERE region = 'public';

GRANT SELECT ON VIEW my_db.analytics.shared_metrics TO SHARE analytics_share;

-- Add consumer account
ALTER SHARE analytics_share ADD ACCOUNTS = consumer_account;
```

## Constraints

### Mandatory Rules (MUST)

1. **RBAC always** — Never grant privileges directly to users
2. **Network policy in production** — Account-level IP restriction required
3. **Mask PII columns** — Apply masking policies to all PII/PHI data
4. **FUTURE GRANTS** — Auto-apply grants to new objects
5. **Audit logging** — Monitor ACCESS_HISTORY and LOGIN_HISTORY weekly
6. **Secure views for sharing** — Never share base tables directly

### Prohibited Actions (MUST NOT)

1. **No ACCOUNTADMIN for daily work** — Use functional roles
2. **No inline credentials** — Use STORAGE_INTEGRATION, KEY_PAIR authentication
3. **No public shares without secure views** — Row-level filtering required
4. **No wildcard grants** — `GRANT ALL` is never acceptable
5. **No disabled MFA for ACCOUNTADMIN** — MFA mandatory for admin roles

## Snowflake Security Checklist

```markdown
- [ ] RBAC role hierarchy defined and documented
- [ ] Network policy applied at account level
- [ ] MFA enabled for ACCOUNTADMIN and SECURITYADMIN
- [ ] Masking policies on all PII/PHI columns
- [ ] Row access policies where multi-tenant data exists
- [ ] Object tags for data classification
- [ ] FUTURE GRANTS configured for all schemas
- [ ] Service accounts use KEY_PAIR authentication (not passwords)
- [ ] Resource monitors with credit alerts
- [ ] ACCESS_HISTORY and LOGIN_HISTORY monitored
- [ ] Secure views used for all data shares
- [ ] IP allowlist reviewed quarterly
```

## Common Issues

### Issue 1: Role Explosion

**Symptom**: Too many roles, hard to manage

**Solution**: Use role hierarchy with functional (what) + access (who) pattern:
```
ACCOUNTADMIN
  └── DATA_ADMIN
        ├── DATA_ENGINEER
        │     └── DATA_WRITER
        │           └── DATA_READER
        └── DATA_SCIENTIST (inherits DATA_READER)
```

### Issue 2: Masking Policy Conflicts

**Symptom**: Error when applying multiple masking policies

**Solution**: One masking policy per column. Use conditional logic within a single policy:
```sql
CREATE MASKING POLICY flexible_mask AS (val STRING)
RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('DATA_ADMIN') THEN val
        WHEN CURRENT_ROLE() IN ('DATA_ENGINEER') THEN SHA2(val)
        ELSE '***MASKED***'
    END;
```

### Issue 3: Service Account Security

**Symptom**: Service accounts using password authentication

**Solution**: Use key pair authentication:
```sql
ALTER USER etl_service SET RSA_PUBLIC_KEY = 'MIIBIjANBg...';
ALTER USER etl_service SET MUST_CHANGE_PASSWORD = FALSE;
```

## References

- [Snowflake Security Overview](https://docs.snowflake.com/en/user-guide/security-overview)
- [Snowflake RBAC](https://docs.snowflake.com/en/user-guide/security-access-control-overview)
- [Dynamic Data Masking](https://docs.snowflake.com/en/user-guide/security-column-ddm-intro)
- [Row Access Policies](https://docs.snowflake.com/en/user-guide/security-row-intro)
- [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies)
