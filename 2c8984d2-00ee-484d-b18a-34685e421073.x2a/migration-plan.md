# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 6 custom profiles, 1 utility module, 1 stub library, 3 roles, and complex Hiera hierarchy management. The migration involves converting modular Puppet profiles following the roles-and-profiles pattern into Ansible roles and playbooks. This is a medium-complexity migration requiring 6-8 weeks for a team of 2-3 engineers, with special attention needed for Hiera's 21-level hierarchy, PuppetDB discovery patterns, encrypted secrets, and cross-module dependencies.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, custom functions (ensure_value, normalize_port), custom types (ensure_value, log_level, port), Facter facts (base_utils_info), Bolt tasks (check_service), and Bolt plans (health_check, rolling_restart) with cross-module function sharing, MOTD management, and OS-specific package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions for data validation, custom types for parameter typing, Facter custom fact collection, Bolt task/plan orchestration, ERB template for MOTD, Hiera hierarchy with OS family support (RedHat, Debian)

**profile_app_stack**:
- Description: Full application stack profile orchestrating Python FastAPI/Uvicorn application deployment with Git repository cloning, virtualenv management, PostgreSQL database provisioning (user, database, privileges), systemd service configuration, Alembic database migrations, log rotation, environment-specific configuration via templates, health checks, and Prometheus monitoring integration with virtual resources
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Strict dependency chaining (Python → Database → App → Service → Monitoring), vcsrepo Git cloning with revision pinning, pip virtualenv with requirements.txt installation, PostgreSQL database creation/user provisioning via psql exec, custom Puppet function (app_db_url) for database URL generation, ERB template for .env file, EPP template for systemd unit, cron-based backups, virtual resource pattern for environment-conditional monitoring (prometheus-node-exporter, prometheus-pushgateway only realized in production), Alembic migrations with onlyif guards

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, deep-merged Hiera backend configuration, dynamic PuppetDB node discovery, SSL/TLS termination configuration, stats page with authentication, firewall management (firewalld/ufw conditional), custom error pages (408, 503), stick-table session persistence, health checks with configurable intervals, and systemd service override for conf.d fragment loading
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy (per-node, role, cluster, app tier, environment, datacenter, region, OS family, etc.) with deep merge for backends hash, PuppetDB queries for dynamic backend discovery with exported resources, ERB template for main haproxy.cfg, EPP template for per-backend configuration fragments, firewall provider abstraction (firewalld vs ufw with exec-based port opening), SELinux boolean management (haproxy_connect_any), config validation before service restart, custom error page deployment, logrotate configuration, systemd override for multi-config loading

**profile_postgresql**:
- Description: PostgreSQL installation profile with PGDG repository configuration, version pinning (15/16 configurable via Hiera), OS-specific package management, and service lifecycle management
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG APT repository configuration with GPG key verification, version-aware package naming (postgresql-{version}, postgresql-contrib-{version}), OS-conditional Hiera data (Debian vs Ubuntu), libpq-dev development library installation, service management with dependency ordering (repo → install → service)

**profile_redis_cluster**:
- Description: Redis cluster profile using puppet-redis module with PuppetDB node discovery for cluster member identification, custom Facter fact (redis_role) for node role detection, maxmemory/eviction policy configuration, and AOF persistence with fsync settings
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query for cluster member discovery, puppet-redis module integration with bind address configuration, requirepass authentication, maxmemory limit with allkeys-lru policy, appendonly AOF with everysec fsync, custom Facter fact (redis_role.rb) for role determination

**profile (wrapper profiles)**:
- Description: Thin wrapper profiles providing composition layer between roles and feature modules, delegating to profile_app_stack, profile_haproxy, and profile_redis_cluster modules with environment fact passing
- Path: site-modules/profile/manifests
- Technology: Puppet
- Key Features: Role composition (base::base, loadbalancer::haproxy, cache::redis, app::stack), common base OS profile with chrony NTP, rsyslog logging, and base_utils integration, environment fact extraction and parameter passing

**role (role definitions)**:
- Description: Role definitions implementing the roles-and-profiles pattern for app_server (base + haproxy + app_stack + redis), app_stack (base + app_stack), haproxy (base + haproxy), and redis_cluster (base + redis) with Linux kernel detection and exec path defaults
- Path: site-modules/role/manifests
- Technology: Puppet
- Key Features: Multi-profile composition for complex node configurations, dependency ordering between profiles (base → feature profiles), kernel-conditional exec path configuration, namespace containment with :: prefix for profile classes

**puppetdb_query_stub**:
- Description: Stub implementation of PuppetDB query function for testing/development environments without PuppetDB, providing mock puppetdb_query function that returns empty arrays
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet (Ruby function)
- Key Features: Ruby-based Puppet function providing puppetdb_query stub for offline/test environments

### Infrastructure Files

- `Puppetfile`: Control repository Puppetfile declaring 9 external Puppet Forge dependencies (stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, apt) with version pinning
- `environment.conf`: Puppet environment configuration defining modulepath with site-modules, modules, and $basemodulepath search order
- `hiera.yaml`: Control repository Hiera configuration (version 5) with 4-level hierarchy (per-node, per-OS family, per-environment, common) using trusted.certname and facts
- `manifests/site.pp`: Site manifest with default node classification including test_git_repo class (creates test repository with app.py, requirements.txt, alembic.ini), role::app_server inclusion, and dependency ordering
- `data/common.yaml`: Global Hiera data with NTP configuration, SSH hardening parameters, syslog settings, profile_haproxy defaults, profile_app_stack application configuration (8 database parameters, 7 application parameters, 4 worker parameters), profile_postgresql version specification, and profile_redis_cluster credentials
- `data/environment/production.yaml`: Production environment Hiera overrides for NTP servers (internal prod servers) and syslog server configuration
- `data/environment/staging.yaml`: Staging environment Hiera overrides (exists but content not examined)
- `site-modules/*/hiera.yaml`: Module-level Hiera configurations with varying hierarchy depths:
  - `base_utils/hiera.yaml`: 3-level OS-aware hierarchy (OS name/release, OS family, common)
  - `profile_haproxy/hiera.yaml`: 21-level enterprise hierarchy (node, role, cluster, app tier, application, team, business unit, lifecycle, environment, network zone, datacenter, region, country, architecture, OS release variants, kernel, container detection, virtual/physical, common)
  - `profile_app_stack/hiera.yaml`: 2-level simple hierarchy (environment, common)
- `site-modules/*/metadata.json`: Puppet module metadata files declaring dependencies, OS support, Puppet version requirements, authors, and semantic versioning
- `site-modules/*/Puppetfile`: Module-specific Puppetfiles for profile_haproxy (stdlib, concat, firewall) and profile_redis_cluster (stdlib, redis, apt)
- `site-modules/base_utils/templates/motd.erb`: ERB template for message-of-the-day with Puppet variables
- `site-modules/profile_app_stack/templates/app.env.erb`: ERB template for application environment file (.env) with database URL, secret key, log level, and API configuration
- `site-modules/profile_app_stack/templates/app.service.epp`: EPP template for systemd unit file with Gunicorn/Uvicorn worker configuration
- `site-modules/profile_app_stack/templates/logrotate.conf.erb`: ERB template for application log rotation configuration
- `site-modules/profile_haproxy/templates/haproxy.cfg.erb`: ERB template for main HAProxy configuration with global settings, stats page, and frontend definitions
- `site-modules/profile_haproxy/templates/backend.conf.epp`: EPP template for HAProxy backend configuration fragments with health check, balance algorithm, and server loop
- `site-modules/profile_redis_cluster/templates/redis.conf.erb`: ERB template for Redis configuration (referenced but not examined)
- `site-modules/profile_app_stack/files/backup.sh`: Shell script for PostgreSQL database backups (pg_dump wrapper)
- `site-modules/profile_app_stack/files/healthcheck.sh`: Shell script for application health checking via HTTP endpoint, with optional metrics pushing
- `site-modules/profile_haproxy/files/haproxy_errors/408.http`: Custom HTTP 408 error page for HAProxy timeout responses
- `site-modules/profile_haproxy/files/haproxy_errors/503.http`: Custom HTTP 503 error page for HAProxy service unavailable responses
- `site-modules/base_utils/lib/facter/base_utils_info.rb`: Custom Facter fact providing platform information for base_utils module
- `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`: Custom Facter fact for HAProxy version detection
- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`: Custom Facter fact for Redis node role identification in cluster
- `site-modules/profile_app_stack/lib/puppet/functions/profile_app_stack/app_db_url.rb`: Custom Puppet function (Ruby) constructing PostgreSQL connection URL from parameters (user, password, host, port, database)
- `site-modules/base_utils/functions/ensure_value.pp`: Puppet language function for value validation and defaulting
- `site-modules/base_utils/functions/normalize_port.pp`: Puppet language function for port number normalization (String → Integer conversion)
- `site-modules/base_utils/types/ensure_value.pp`: Custom Puppet type for ensure parameter validation
- `site-modules/base_utils/types/log_level.pp`: Custom Puppet type for log level enumeration validation
- `site-modules/base_utils/types/port.pp`: Custom Puppet type for port number validation (1-65535 range)
- `site-modules/base_utils/tasks/check_service.json`: Bolt task metadata for service health checking
- `site-modules/base_utils/tasks/check_service.sh`: Bolt task implementation for service status verification
- `site-modules/base_utils/plans/health_check.pp`: Bolt plan orchestrating multi-node health checks
- `site-modules/base_utils/plans/rolling_restart.pp`: Bolt plan implementing rolling restart pattern across node groups
- `Vagrantfile`: Vagrant configuration for local testing/development environment
- `vagrant-provision.sh`: Vagrant provisioning script for initial VM setup
- `test/Containerfile`: Container definition for testing Puppet code
- `test/run.sh`: Test execution script for containerized testing

### Target Details

Based on the Puppet source configuration:

- **Operating System**: RedHat Enterprise Linux 9, Ubuntu 24.04, or Debian 12 (multi-OS support detected via Hiera os/%{facts.os.family}.yaml and metadata.json operatingsystem_support declaring RedHat 8/9, Debian 11/12, Ubuntu 22.04/24.04)
- **Virtual Machine Technology**: Not specified in configuration files, likely KVM or VMware based on enterprise Puppet control repository patterns
- **Cloud Platform**: Not cloud-specific; designed for on-premises or cloud-agnostic deployment (no AWS/Azure/GCP-specific configurations detected)

## Migration Approach

### Key Dependencies to Address

External Puppet Forge modules requiring Ansible equivalents:

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible core modules and community.general collection for file manipulation, fact handling, and type validation
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template module using Jinja2 templating and assemble module for fragment concatenation
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld and community.general.ufw modules for firewall management
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module for Git repository management
- **puppet-redis (11.0.0)**: Replace with community.general.redis or davidwittman.redis Ansible role with custom configuration management
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module for service management and systemd unit file deployment
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module for INI file manipulation
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and ansible.builtin.apt_key modules for APT repository management
- **PuppetDB queries**: Replace with Ansible dynamic inventory (AWX/Tower), service discovery (Consul), or static inventory with group_vars; puppetdb_query() calls require architectural redesign for node discovery

### Security Considerations

Critical security configurations requiring careful migration:

- **Encrypted Hiera data (EYAML)**: Database passwords, HAProxy stats password, Redis password, application secret keys are encrypted with PKCS7 (ENC[PKCS7,...]) in Hiera YAML files. Migrate to Ansible Vault for secrets management with ansible-vault encrypt_string. Identified encrypted credentials in:
  - `profile_haproxy::stats_password` (HAProxy admin interface)
  - `profile_app_stack::db_password` (PostgreSQL database password)
  - `profile_redis_cluster::redis_password` (Redis requirepass authentication)
  - Total: 3 encrypted secrets requiring vault migration
- **SSL/TLS certificates**: HAProxy SSL configuration references ssl_cert_path and ssl_key_path for certificate/key storage. Migrate certificate deployment with ansible.builtin.copy with mode 0600/0640 and validate parameter for certificate verification
- **SSH hardening**: SSH configuration (permit_root_login: false, client_alive_interval: 300) defined in common.yaml requires migration to ansible.posix.sshd_config or community.general.sshd module
- **Service authentication**: PostgreSQL user/password provisioning via psql exec commands with password interpolation requires secure migration using postgresql_user module with no_password_changes parameter or vault-encrypted credentials
- **File permissions**: Security-sensitive files (.env with mode 0600, HAProxy configs with mode 0640, SSL keys) require explicit mode preservation in Ansible tasks
- **Secrets in templates**: Template files (app.env.erb, haproxy.cfg.erb) interpolate passwords and secret keys; ensure Jinja2 templates use vault variables with no_log: true task parameter
- **SELinux management**: HAProxy SELinux boolean (haproxy_connect_any) requires ansible.posix.seboolean module in RHEL environments

### Technical Challenges

1. **Hiera 21-level hierarchy complexity**: profile_haproxy uses 21-level Hiera hierarchy (node, role, cluster, app tier, application, team, business unit, lifecycle, environment, network zone, datacenter, region, country, architecture, OS variants, kernel, container detection, virtual/physical). Migration strategy:
   - Map to Ansible inventory hierarchy (group_vars, host_vars) with nested groups
   - Use multiple variable precedence levels (all → datacenter → environment → cluster → host)
   - Consider ansible-cmdb or custom inventory scripts for complex hierarchy
   - Document variable precedence clearly (Ansible has 22 precedence levels vs Puppet's Hiera merge)

2. **Deep merge hash patterns**: profile_haproxy::backends uses deep merge across hierarchy levels to compose backend server lists. Migration strategy:
   - Use hash_behaviour=merge in ansible.cfg (deprecated, not recommended)
   - Or redesign using combine filter in Jinja2: `{{ defaults | combine(overrides, recursive=True) }}`
   - Or use group_vars with explicit variable layering (backends_base, backends_env, backends_cluster merged in playbook)

3. **PuppetDB dynamic discovery**: profile_haproxy::discover and profile_redis_cluster use PuppetDB queries for node discovery. Migration strategy:
   - Replace with Ansible dynamic inventory (if using AWX/Tower/Semaphore)
   - Or use service discovery (Consul with community.general.consul_kv, etcd, or DNS SRV records)
   - Or implement custom dynamic inventory script querying infrastructure CMDB/API
   - Exported resources (@@haproxy::balancermember) require host facts cached in inventory or database

4. **Custom Puppet functions**: Ruby functions (app_db_url.rb), Puppet language functions (ensure_value.pp, normalize_port.pp). Migration strategy:
   - Reimplement as Jinja2 filters or custom Ansible filter plugins
   - app_db_url: Use Jinja2 string template `postgresql://{{ user }}:{{ pass }}@{{ host }}:{{ port }}/{{ db }}`
   - normalize_port: Use Jinja2 int filter `{{ port | int }}`
   - ensure_value: Use Jinja2 default filter `{{ value | default(fallback) }}`

5. **Custom Facter facts**: Ruby facts (base_utils_info.rb, haproxy_version.rb, redis_role.rb). Migration strategy:
   - Reimplement as Ansible custom facts (/etc/ansible/facts.d/*.fact as executable JSON/INI)
   - Or use ansible.builtin.setup module with fact_path parameter
   - Or integrate into roles as set_fact tasks based on command outputs
   - HAProxy version detection: `shell: haproxy -v | awk '{print $3}'` → set_fact

6. **Bolt tasks and plans**: base_utils includes Bolt tasks (check_service) and plans (health_check, rolling_restart). Migration strategy:
   - Migrate Bolt tasks to Ansible ad-hoc commands or roles
   - Migrate Bolt plans to Ansible playbooks with serial/delegation patterns
   - rolling_restart plan → Ansible playbook with serial: 1 and health check handlers
   - health_check plan → Ansible playbook with uri module or script module

7. **Virtual resources pattern**: profile_app_stack::monitoring uses virtual resources (@package, @service) realized only in production environment. Migration strategy:
   - Use Ansible conditionals: `when: ansible_environment == 'production'`
   - Or use inventory groups (production group) with group_vars
   - Or use tags for environment-specific tasks: `--tags production-monitoring`

8. **Strict dependency chaining**: profile_app_stack uses strict dependency chain (Python → Database → App → Service → Monitoring) with notify/require relationships. Migration strategy:
   - Use Ansible handlers for restart notifications (notify: restart app)
   - Use block structure with rescue for error handling
   - Maintain task ordering within role tasks/main.yml
   - Use meta: flush_handlers for immediate handler execution between phases

9. **Service validation and checks**: HAProxy performs config validation (haproxy -c) before restart. Migration strategy:
   - Use validate parameter in template module: `validate: 'haproxy -c -f %s'`
   - Use command module with changed_when/failed_when for validation
   - Implement pre-flight checks in separate task before service restart

10. **Multi-OS support**: Modules support RedHat/Debian families with OS-specific Hiera data. Migration strategy:
    - Use ansible_os_family fact in when conditionals
    - Create OS-specific variable files (vars/RedHat.yml, vars/Debian.yml)
    - Use ansible.builtin.include_vars with files parameter for OS detection
    - Package name mapping (vim-enhanced vs vim, dnsutils vs bind-utils)

### Migration Order

Suggested migration sequence based on dependencies and risk:

1. **base_utils** (1 week): Low risk, high value foundation module
   - No external profile dependencies
   - Provides common types and functions used by other modules
   - Custom functions → Jinja2 filters
   - Custom facts → Ansible facts.d
   - Bolt tasks → Ansible playbooks
   - Template MOTD → Jinja2 template
   - Utility packages → package module with OS conditionals

2. **profile_postgresql** (1 week): Moderate complexity, foundational database service
   - Standalone service with minimal dependencies
   - APT repository management → apt_repository module
   - Version pinning → package module with version parameter
   - Service management → systemd module
   - Required by profile_app_stack but can be tested independently

3. **profile_redis_cluster** (1.5 weeks): Moderate complexity, requires PuppetDB redesign
   - Depends on puppet-redis (community role equivalent)
   - PuppetDB query requires dynamic inventory or service discovery implementation
   - Custom Facter fact → Ansible fact script
   - Redis configuration → template module
   - Test standalone before integrating with roles

4. **profile_app_stack** (2 weeks): High complexity, multiple dependencies
   - Depends on profile_postgresql for database provisioning
   - Vcsrepo → git module for repository cloning
   - Virtualenv management → pip module with virtualenv parameter
   - Template complexity (ERB → Jinja2): app.env.erb, app.service.epp, logrotate.conf.erb
   - Database provisioning → postgresql_user, postgresql_db modules
   - Custom function (app_db_url) → Jinja2 template expression
   - Systemd service → systemd module with template
   - Virtual resources → conditional tasks
   - Strict dependency chain → block/rescue structure
   - Alembic migrations → command module with creates/onlyif logic

5. **profile_haproxy** (2 weeks): Highest complexity, 21-level Hiera hierarchy
   - Deep merge hash patterns require careful variable composition
   - 21-level Hiera hierarchy → multi-level group_vars/host_vars
   - PuppetDB discovery → dynamic inventory or service discovery
   - Firewall provider abstraction → conditional tasks (firewalld vs ufw)
   - ERB/EPP templates → Jinja2 templates with loops
   - Backend hash loop → Jinja2 for loop in template or with_dict in tasks
   - SELinux boolean → seboolean module
   - Config validation → template validate parameter
   - Systemd override → systemd unit fragment with drop-in
   - Custom error pages → copy module
   - Exported resources → inventory-based approach

6. **profile wrapper layer** (0.5 weeks): Low complexity, thin delegation layer
   - Simple class includes → role dependencies or include_role
   - Environment fact passing → ansible_environment variable
   - May be consolidated into roles directly

7. **role definitions** (0.5 weeks): Low complexity, composition layer
   - Multi-profile composition → Ansible role dependencies
   - Dependency ordering → meta/main.yml dependencies
   - Kernel conditionals → when clauses
   - May reorganize into Ansible role structure directly

8. **Hiera data migration** (1 week): Critical for all modules
   - common.yaml → group_vars/all.yml
   - environment/*.yaml → group_vars/production.yml, group_vars/staging.yml
   - Module data → role defaults/main.yml and vars/main.yml
   - Encrypted data → Ansible Vault with ansible-vault encrypt_string
   - Deep merge strategy → combine filter or inventory group nesting

9. **Integration testing** (1 week): Validate end-to-end workflows
   - Test role::app_server composition (base + haproxy + app_stack + redis)
   - Test role::app_stack (base + app_stack)
   - Test role::haproxy (base + haproxy)
   - Test role::redis_cluster (base + redis)
   - Validate secret encryption/decryption
   - Verify service dependencies and ordering
   - Test multi-OS support (RedHat 9, Ubuntu 24.04, Debian 12)

**Timeline estimate**: 6-8 weeks for a team of 2-3 engineers, assuming parallel module development and dedicated testing time.

### Assumptions

1. **PuppetDB replacement**: Assumes dynamic inventory solution (AWX/Tower) or service discovery infrastructure (Consul, etcd) will replace PuppetDB queries. Static inventory is insufficient for dynamic backend discovery patterns.

2. **EYAML key availability**: Assumes access to Puppet EYAML private key for decrypting existing encrypted Hiera data before re-encrypting with Ansible Vault. If key is unavailable, credentials must be reset.

3. **Certificate management**: SSL/TLS certificates referenced in HAProxy configuration (ssl_cert_path, ssl_key_path) are assumed to exist and be accessible for migration. Certificate renewal/management process (Let's Encrypt, manual, external PKI) is not clear from configuration.

4. **Git repository access**: profile_app_stack clones from app_repo (https://github.com/example-org/myapp-api.git or file:///tmp/test-app-repo). Migration assumes continued access to Git repositories or migration to alternative deployment method (artifact repository, container registry).

5. **PostgreSQL cluster vs standalone**: profile_postgresql installs PostgreSQL but lacks replication, backup, or HA configuration. Assumes single-instance PostgreSQL is sufficient; if HA/replication is required, additional roles needed.

6. **Redis cluster architecture**: profile_redis_cluster references cluster in name and uses PuppetDB for node discovery, but redis.pp only configures standalone Redis with AOF persistence. Unclear if true Redis Cluster (cluster-enabled yes) or Redis Sentinel/replication is intended; assumes standalone Redis with future clustering capability.

7. **Monitoring integration**: profile_app_stack references Prometheus node-exporter and pushgateway but lacks full observability stack (Prometheus server, Grafana). Assumes monitoring infrastructure exists separately or will be deployed independently.

8. **Firewall state management**: profile_haproxy supports firewalld/ufw but uses exec-based port opening without idempotent state checking (unless clauses may be brittle). Assumes firewall rules can be rewritten with proper Ansible modules for idempotency.

9. **Hiera hierarchy levels**: profile_haproxy's 21-level hierarchy references custom facts (cluster_name, app_tier, team, business_unit, network_zone, datacenter, region, country, lifecycle) not present in standard Facter. Assumes these facts are populated by external fact scripts, ENC (External Node Classifier), or will be migrated to inventory variables.

10. **Bolt task/plan usage**: base_utils includes Bolt tasks and plans, but their production usage frequency is unclear. Assumes these are used for operational tasks (health checks, rolling restarts) and should be migrated to Ansible equivalents (playbooks, ad-hoc commands).

11. **Test environment**: Vagrantfile and test/ directory suggest local testing capability. Assumes Vagrant environment can be replaced with Molecule + Docker/Podman for Ansible role testing.

12. **Service discovery protocol**: Unclear how HAProxy backend discovery determines backend server health, IP addresses, and ports from PuppetDB queries. Assumes exported resources or fact-based discovery; migration requires architectural decision on service registry approach.

13. **Alembic migration workflow**: profile_app_stack runs Alembic database migrations (alembic upgrade head) with onlyif guard. Assumes migrations are idempotent and safe for repeated execution; unclear if migrations require downtime or rolling deployment strategy.

14. **Virtual resource realization**: profile_app_stack uses Puppet virtual resources (@package, @service) realized only in production. Assumes this environment-conditional pattern should be preserved in Ansible (not deploy monitoring in staging/dev).

15. **Systemd-only assumption**: All service management uses systemd (systemd unit files, systemctl commands). Assumes target systems are systemd-based (RHEL 7+, Ubuntu 16.04+, Debian 8+); no SysV init or Upstart support detected.

16. **Database credential rotation**: Database passwords are encrypted in Hiera but no credential rotation logic exists. Assumes credentials are static and rotated manually; migration should consider automated rotation if required by security policy.

17. **HAProxy backend health checks**: Backend configurations reference health_check (httpchk GET /health) but application health check endpoint implementation is not visible in Puppet code. Assumes applications expose /health endpoints compatible with HAProxy httpchk.

18. **Log aggregation**: Syslog server configuration (syslog::server, syslog::facility) suggests centralized logging but no log shipper (rsyslog, Fluentd, Filebeat) configuration is present. Assumes log aggregation is handled externally or will be added post-migration.

19. **Backup retention**: Database backup script (backup.sh) runs daily via cron but no backup retention, compression, or offsite storage logic is visible. Assumes backup management needs enhancement or is handled by external backup system.

20. **Multi-environment Hiera data completeness**: Only common.yaml and production.yaml were examined; staging.yaml exists but content is unknown. Assumes staging environment has similar structure to production with environment-specific overrides.
