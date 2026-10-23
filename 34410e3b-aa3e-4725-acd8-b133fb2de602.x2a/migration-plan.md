# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository with a roles-and-profiles pattern implementation managing a multi-tier application stack infrastructure. The migration involves 5 custom Puppet modules, 4 role definitions, and a complex 21-level Hiera hierarchy for the HAProxy module. The codebase demonstrates enterprise-grade practices including PuppetDB integration for dynamic discovery, custom Puppet functions, Bolt tasks, virtual resources for conditional provisioning, and encrypted secrets management. Estimated migration timeline: 6-8 weeks for full implementation and testing.

## Module Migration Plan

This repository contains Puppet modules following the roles-and-profiles pattern that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Foundation utility module providing common helpers including message-of-the-day management, custom defined types (config_entry, create_dir, managed_notify), Puppet functions (ensure_value, normalize_port), custom Facter facts (platform_info), Bolt tasks and plans (health_check, rolling_restart, check_service), and OS-specific utility package management with Hiera support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Module-level Hiera hierarchy with OS-specific data, custom Ruby Facter fact, Bolt task execution framework, Puppet 4.x function API (ensure_value.pp, normalize_port.pp), typed parameters (ensure_value type, log_level type, port type), external facts in facts.d/

**profile_app_stack**:
- Description: Full-stack Python web application deployment orchestrating Python 3 runtime, PostgreSQL database provisioning, Git repository cloning via vcsrepo, Python virtualenv creation, pip dependency installation, Alembic database migrations, systemd service management, Gunicorn/Uvicorn worker configuration, environment file templating, health check scripts, log rotation, cron-based database backups, and Prometheus monitoring integration with conditional realization in production
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Strict dependency chain (python → database → app → service → monitoring), custom Puppet Ruby function for PostgreSQL URL construction with password encoding, integration with profile_postgresql module, virtual resources for monitoring (@package, @service, @cron) realized only in production, dynamic database user/database creation with privilege grants, Alembic migration execution, FastAPI/Uvicorn application support, logrotate configuration via ERB template, systemd service templating with EPP

**profile_haproxy**:
- Description: HAProxy load balancer with 21-level Hiera hierarchy supporting per-node, per-cluster, per-datacenter, per-environment configuration; multi-backend support via deep hash merging; PuppetDB-based dynamic backend discovery using exported resources and PuppetDB queries; SSL/TLS termination with configurable ciphers and minimum TLS version; statistics page with authentication; custom error page deployment (503, 408); firewall rule management; session persistence via stick-tables; health check configuration per backend
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy (node/cluster/datacenter/region/environment/OS/architecture), deep merge backends hash from multiple Hiera levels, PuppetDB query integration for dynamic server discovery, exported resources (@@haproxy::balancermember), conditional stick-table configuration (production only), iterative backend configuration generation, concat-based configuration assembly, module-level Puppetfile, custom Facter fact (haproxy_version), firewall integration via puppetlabs-firewall

**profile_postgresql**:
- Description: PostgreSQL 15 installation and configuration using PostgreSQL Global Development Group (PGDG) official repository with apt module integration for Debian/Ubuntu systems, version pinning, package management, and service orchestration
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG repository configuration via puppetlabs-apt, version-specific package installation, service management with strict dependency ordering (repo → install → service), Debian/Ubuntu 24.04 LTS support

**profile_redis_cluster**:
- Description: Redis cluster configuration using puppet-redis module with PuppetDB integration for cluster node discovery, dynamic node detection via PuppetDB queries, password-protected instances, memory management (maxmemory policies), and custom Redis configuration templating
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query for cluster member discovery, custom Redis Facter fact (redis_role), ERB template for redis.conf, integration with puppet-redis module (v11.0.0), allkeys-lru eviction policy, module-level Puppetfile

**profile::base::base**:
- Description: Base operating system profile providing common infrastructure services including chrony NTP time synchronization, rsyslog logging service, and base_utils module integration; applied to all node types as foundation layer in roles-and-profiles pattern
- Path: site-modules/profile/manifests/base/base.pp
- Technology: Puppet
- Key Features: Conditional service management based on kernel fact (Linux-only), parameterized service enablement via Hiera lookup, dependency for all role classes

**profile::app::stack**:
- Description: Thin wrapper profile delegating to profile_app_stack module, providing application stack provisioning with environment-based configuration
- Path: site-modules/profile/manifests/app/stack.pp
- Technology: Puppet
- Key Features: Class delegation pattern, environment fact integration

**profile::cache::redis**:
- Description: Thin wrapper profile delegating to profile_redis_cluster module for Redis cluster deployment
- Path: site-modules/profile/manifests/cache/redis.pp
- Technology: Puppet
- Key Features: Class delegation pattern, environment fact integration

**profile::loadbalancer::haproxy**:
- Description: Thin wrapper profile delegating to profile_haproxy module for HAProxy load balancer deployment
- Path: site-modules/profile/manifests/loadbalancer/haproxy.pp
- Technology: Puppet
- Key Features: Class delegation pattern, environment fact integration

**role::app_server**:
- Description: Application server role composing base profile with HAProxy load balancer, application stack, and Redis cache; represents a complete multi-tier application server node
- Path: site-modules/role/manifests/app_server.pp
- Technology: Puppet
- Key Features: Multi-profile composition (base + loadbalancer + app + cache), exec path default setting for Linux

**role::app_stack**:
- Description: Application stack role for dedicated application nodes with PostgreSQL database integration, excluding load balancer and cache layers; ensures base profile completes before application provisioning
- Path: site-modules/role/manifests/app_stack.pp
- Technology: Puppet
- Key Features: Dependency ordering (base → app_stack), kernel-based exec path configuration

**role::haproxy**:
- Description: Dedicated HAProxy load balancer role combining base OS profile with HAProxy configuration; designed for standalone load balancer nodes
- Path: site-modules/role/manifests/haproxy.pp
- Technology: Puppet
- Key Features: Two-profile composition (base + loadbalancer), strict dependency ordering

**role::redis_cluster**:
- Description: Dedicated Redis cluster node role combining base profile with Redis cluster configuration
- Path: site-modules/role/manifests/redis_cluster.pp
- Technology: Puppet
- Key Features: Two-profile composition (base + cache), strict dependency ordering

**puppetdb_query_stub**:
- Description: Development/testing stub for PuppetDB query function that returns empty arrays when PuppetDB is unavailable, enabling local testing without full PuppetDB infrastructure
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Ruby function stub (puppetdb_query), warning message for missing PuppetDB, facilitates Vagrant/test environment execution

### Infrastructure Files

- **Puppetfile**: Forge module dependencies (puppetlabs-stdlib 9.7.0, puppetlabs-concat 9.0.2, puppetlabs-firewall 8.1.3, puppetlabs-vcsrepo 6.1.0, puppet-redis 11.0.0, puppet-systemd 7.1.0, puppetlabs-inifile 6.1.1, puppetlabs-apt 9.4.0); must be replaced with Ansible Galaxy/collection equivalents
- **environment.conf**: Defines modulepath with site-modules precedence over upstream modules; critical for understanding module loading order
- **hiera.yaml**: Environment-level Hiera hierarchy (4 levels: per-node → per-OS → per-environment → common); combine with module-level hierarchies for complete data resolution picture
- **manifests/site.pp**: Site manifest with node default classification applying test_git_repo class and role::app_server; creates test git repository with Python FastAPI application, requirements.txt, and Alembic configuration for Vagrant/testing
- **data/common.yaml**: Environment-level common defaults including NTP servers, SSH hardening, syslog configuration, and base parameter values for all profile modules with plaintext test passwords
- **data/environment/production.yaml**: Production overrides for NTP servers (ntp1.prod.internal, ntp2.prod.internal) and syslog server (syslog.prod.internal)
- **data/environment/staging.yaml**: Staging environment overrides (file exists but not read, assumed similar structure to production)
- **Vagrantfile**: Local development/testing environment definition; likely configures VMs for testing Puppet code
- **vagrant-provision.sh**: Vagrant provisioning script for bootstrapping Puppet agent in development environment
- **test/Containerfile**: Container-based testing infrastructure (likely Puppet-in-Docker for CI/CD)
- **test/run.sh**: Test execution script for containerized testing

### Target Details

Based on the Puppet module configurations and metadata.json files:

- **Operating System**: Red Hat Enterprise Linux 9 / Ubuntu 24.04 LTS (profile_app_stack metadata specifies RHEL 8/9 and Ubuntu 22.04/24.04; profile_haproxy supports RHEL 8/9 and Debian 11/12; profile_postgresql targets Ubuntu 24.04 and Debian 12; base_utils supports RHEL 8/9, Debian 11/12, Ubuntu 22.04/24.04). Default to RHEL 9 for production deployment.
- **Virtual Machine Technology**: Not explicitly specified in Puppet code; base_utils includes facts for virtual vs physical detection and container detection via facts.is_virtual. Likely targets VMware or KVM based on enterprise pattern usage.
- **Cloud Platform**: No cloud-specific resources detected. Infrastructure appears cloud-agnostic but could be deployed to AWS/Azure/GCP. HAProxy datacenter/region hierarchy suggests potential multi-cloud or multi-datacenter deployment model.

## Migration Approach

### Key Dependencies to Address

External Puppet Forge modules that require Ansible equivalents:

- **puppetlabs-stdlib (9.7.0)**: Core Puppet functions and types used throughout all modules. Replace with Ansible built-in filters (map, select, json_query) and community.general collection utilities
- **puppetlabs-concat (9.0.2)**: File fragment assembly for HAProxy configuration. Replace with Ansible template module using Jinja2 loops and includes, or assemble module for fragment-based assembly
- **puppetlabs-firewall (8.1.3)**: Firewall rule management in profile_haproxy. Replace with ansible.posix.firewalld or community.general.ufw depending on target OS
- **puppetlabs-vcsrepo (6.1.0)**: Git repository cloning in profile_app_stack. Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Redis installation and configuration in profile_redis_cluster. Replace with community.general.redis role or custom tasks using ansible.builtin.package and ansible.builtin.template
- **puppet-systemd (7.1.0)**: Systemd integration and service management. Replace with ansible.builtin.systemd module and ansible.builtin.systemd_service
- **puppetlabs-inifile (6.1.1)**: INI file manipulation. Replace with community.general.ini_file module
- **puppetlabs-apt (9.4.0)**: APT repository management for PostgreSQL PGDG repo. Replace with ansible.builtin.apt_repository and ansible.builtin.apt_key modules

### Security Considerations

Credential and secret management patterns identified:

- **Hiera-eyaml Encrypted Secrets**: Multiple Hiera YAML files contain ENC[PKCS7,...] encrypted values for sensitive data:
  - profile_app_stack::db_password (database credentials in site-modules/profile_app_stack/data/common.yaml)
  - profile_app_stack::secret_key (application secret key in site-modules/profile_app_stack/data/environment/production.yaml)
  - profile_haproxy::stats_password (HAProxy stats page authentication in site-modules/profile_haproxy/data/common.yaml)
  - Migrate to Ansible Vault encrypted variables or integrate with HashiCorp Vault via community.hashi_vault collection
  - Approximately 4-6 encrypted secrets identified across modules
- **Plaintext Passwords in Test Data**: Development/test credentials stored in plaintext in data/common.yaml:
  - profile_haproxy::stats_password: "test-haproxy-password"
  - profile_app_stack::db_password: "test-db-password"
  - profile_app_stack::secret_key: "test-secret-key"
  - profile_redis_cluster::redis_password: "test-redis-password"
  - These should remain plaintext for testing but production equivalents must use Ansible Vault
- **SSL/TLS Certificate Management**: profile_haproxy references SSL certificate and key paths (ssl_cert_path: /etc/ssl/certs, ssl_key_path: /etc/ssl/private) but does not manage certificate content. Migration must address certificate deployment via ansible.builtin.copy with vault-encrypted certificate files or integration with certificate authority
- **Database Credential Injection**: profile_app_stack::app_db_url custom function URL-encodes database passwords before embedding in DATABASE_URL environment variable. Ansible equivalent must use Jinja2 filters (urlencode) to maintain security and prevent special character issues
- **File Permissions**: Service-specific users and restricted file permissions enforced:
  - HAProxy config files: mode 0640, group haproxy
  - Application .env file: mode 0600, owner appuser
  - SSL keys would require mode 0400, owner root
  - Maintain principle of least privilege in Ansible playbooks using ansible.builtin.file mode parameter

### Technical Challenges

Migration complexity factors requiring careful planning:

- **21-Level Hiera Hierarchy (profile_haproxy)**: Extreme configuration hierarchy with node → role → cluster → app_tier → application → team → business_unit → lifecycle → environment → network_zone → datacenter → region → country → architecture → OS release → OS family/major → OS family → kernel → container → virtual → common levels. 
  - Challenge: Ansible has no direct equivalent to Hiera's automatic hierarchical data lookup
  - Solution: Implement using Ansible's variable precedence with group_vars directory structure (group_vars/all/, group_vars/datacenter_fra/, group_vars/environment_production/, group_vars/os_RedHat/, host_vars/lb01.fra.example.com/) and vars_files includes
  - Consider custom lookup plugin for dynamic hierarchy traversal or simplify hierarchy to 5-7 practical levels (node → cluster → environment → os → common)
  - Document hierarchy reduction decisions for operations team

- **Deep Hash Merging**: profile_haproxy uses Hiera deep merge for backends hash, combining server lists from multiple hierarchy levels
  - Challenge: Ansible combine filter requires explicit merge=True and doesn't replicate Hiera's deep merge behavior across multiple levels
  - Solution: Use hash_behaviour=merge (deprecated) or custom filter plugin, or refactor to use list concatenation with unique filter

- **PuppetDB Dynamic Discovery**: profile_haproxy::discover and profile_redis_cluster use PuppetDB queries to discover cluster members dynamically via puppetdb_query() function and exported resources (@@haproxy::balancermember)
  - Challenge: Ansible has no built-in dynamic inventory system equivalent to exported resources
  - Solution: Replace with Ansible dynamic inventory script querying external CMDB/inventory source, or use add_host module with API queries, or migrate to static inventory with group_by for cluster assignment
  - Exported resources pattern (@@haproxy::balancermember <<| |>>) requires fundamental redesign

- **Custom Puppet Functions**: Ruby-based custom functions require reimplementation:
  - profile_app_stack::app_db_url: PostgreSQL URL builder with password encoding → Ansible filter plugin or Jinja2 template with urlencode filter
  - base_utils functions (ensure_value, normalize_port): Likely validation functions → Ansible assert module or custom filter plugins
  - puppetdb_query stub: Remove entirely, replace with dynamic inventory

- **Virtual Resources and Realization**: profile_app_stack::monitoring declares @package, @service, @cron resources realized only when $facts['environment'] == 'production'
  - Challenge: Ansible has no virtual resource concept
  - Solution: Use when conditionals (when: ansible_environment == 'production') on tasks, or separate playbooks/roles for environment-specific resources

- **Bolt Tasks and Plans**: base_utils includes Bolt tasks (check_service.json, check_service.sh) and plans (health_check.pp, rolling_restart.pp) for operational automation
  - Challenge: Bolt tasks don't translate to Ansible
  - Solution: Reimplement as Ansible ad-hoc commands or playbooks with ansible.builtin.script module for check_service.sh, or migrate to Ansible roles with tags for operational tasks

- **Custom Facter Facts**: Ruby-based custom facts (base_utils_info.rb, haproxy_version.rb, redis_role.rb, platform_info.json) provide dynamic node data
  - Challenge: Facter facts don't exist in Ansible
  - Solution: Reimplement as Ansible custom facts in /etc/ansible/facts.d/ (for static facts) or use set_fact with command/script modules to gather dynamic data

- **Strict Dependency Chaining**: profile_app_stack uses Puppet's chaining arrow (Class['A'] -> Class['B'] ~> Class['C']) for strict ordering with notification
  - Challenge: Ansible uses implicit task ordering but notification is handler-based
  - Solution: Use notify/handlers for service restarts, use pre_tasks/tasks/post_tasks for phase separation, or break into multiple plays with serial execution

- **Template Diversity**: Mix of ERB (.erb) and EPP (.epp) templates across modules
  - Challenge: Must convert all to Jinja2, requiring syntax translation
  - Solution: ERB <%= %> becomes Jinja2 {{ }}, EPP <%=  %> becomes {{ }}, but Ruby method calls in templates need Jinja2 filter equivalents

- **Module-Level Hiera**: Each module (profile_haproxy, profile_app_stack, base_utils) has its own hiera.yaml defining module-specific hierarchies and datadirs
  - Challenge: Ansible has no module-level data hierarchy
  - Solution: Flatten into role-level defaults (roles/<role>/defaults/main.yml) and combine with group_vars, or use include_vars with constructed paths

### Migration Order

Suggested sequence based on dependencies and complexity:

1. **base_utils** (1 week): Foundation module with minimal dependencies; start here to establish patterns for custom facts, utility functions. Simple MOTD management and package installation provides low-risk migration baseline
2. **profile_postgresql** (3-4 days): Simple repository configuration and package installation; no complex dependencies. Establishes pattern for APT repository management
3. **profile_redis_cluster** (1 week): Moderate complexity with PuppetDB integration; can test dynamic discovery patterns early. Remove PuppetDB query and use static inventory initially
4. **profile_app_stack** (2 weeks): High complexity with multiple phases (python → database → app → service → monitoring), custom function, virtual resources. Critical path item requiring Python virtualenv, git, systemd, and database integration
5. **profile_haproxy** (2-3 weeks): Highest complexity due to 21-level Hiera hierarchy, deep hash merging, PuppetDB discovery, exported resources. Requires careful variable precedence design
6. **Wrapper profiles** (profile::base::base, profile::app::stack, etc.) (2-3 days): Thin wrappers become include_role or import_role statements in Ansible
7. **Roles** (role::app_server, role::app_stack, role::haproxy, role::redis_cluster) (1 week): Become Ansible playbooks or parent roles that compose multiple roles; test complete node provisioning
8. **Integration testing** (1 week): Vagrant environment migration, end-to-end testing with production-like configuration

### Assumptions

- **Hiera Encryption Tool**: Assumes hiera-eyaml is used for PKCS7 encryption. Keys/certificates needed to decrypt existing secrets must be provided for migration, or secrets must be re-encrypted using Ansible Vault
- **PuppetDB Availability**: Assumes PuppetDB is available in production for dynamic discovery. Migration may require new CMDB/inventory source or acceptance of static inventory limitations
- **Puppet Version**: Assumes Puppet 7.x based on metadata.json requirements (">= 7.0.0 < 9.0.0"). Code uses modern Puppet 4+ function API and EPP templates
- **Operating System Target**: Primary target appears to be RHEL 8/9 and Ubuntu 22.04/24.04 based on metadata; assumes systemd, apt/yum package managers
- **Git Repository Access**: profile_app_stack clones from git repository (file:///tmp/test-app-repo in test, https://github.com/example-org/myapp-api.git in production). Migration requires Git credentials/SSH keys for private repositories
- **PostgreSQL PGDG Repository**: Assumes continued use of PostgreSQL Global Development Group official repositories rather than OS-provided PostgreSQL packages
- **Monitoring Infrastructure**: profile_app_stack references Prometheus node exporter and pushgateway. Assumes Prometheus infrastructure exists for metric collection
- **Network Connectivity**: HAProxy configuration assumes backend servers are reachable by IP/hostname. Firewall rules may need adjustment during migration
- **Service Account Credentials**: Assumes service accounts (appuser, haproxy user) can be created with same UIDs/GIDs across environment, or UID/GID conflicts are acceptable
- **Systemd Requirement**: Application service management uses systemd unit files. Migration targets must run systemd (eliminates RHEL 6, Ubuntu 14.04, or SysVinit systems)
- **Python 3 Availability**: profile_app_stack requires Python 3, pip, and venv modules. Assumes Python 3.8+ available on target systems
- **Test Environment**: Vagrantfile suggests local testing environment exists. Assumes migration can use similar Vagrant or container-based testing before production deployment
- **No Windows Targets**: All code targets Linux (kernel fact checks, package managers). Assumes no Windows server migration required
- **Change Management Process**: Assumes phased rollout is acceptable (migrate module-by-module rather than big-bang cutover)
- **Backup Strategy**: Assumes existing backup processes for database (profile_app_stack includes daily cron backup). Ansible migration should preserve or improve backup automation
- **SSL Certificate Source**: HAProxy SSL configuration references certificate paths but doesn't show certificate deployment mechanism. Assumes certificates are deployed via separate process or manual steps
- **Log Aggregation**: References to syslog servers and log forwarding suggest centralized logging exists. Ansible migration should preserve rsyslog/syslog-ng forwarding configurations
- **Monitoring Cutover**: Virtual resource realization based on environment fact suggests monitoring is production-only. Assumes staging/development environments don't require full monitoring stack
- **Documentation Gaps**: Not all Hiera data files were examined (staging environment, cluster/datacenter/node-specific overrides). Assumes additional configuration exists that wasn't visible in reviewed files
- **Module Ownership**: Module metadata shows "Platform Team" as author. Assumes single team owns all modules and can coordinate migration without cross-team dependencies
- **Version Pinning**: Puppetfile pins specific versions (puppetlabs-stdlib 9.7.0 vs 9.6.0 in module Puppetfiles). Assumes version conflicts are manageable or can be reconciled during migration
- **Idempotency Requirements**: Puppet ensures idempotency via resource abstraction. Assumes Ansible playbooks must maintain same idempotency guarantees (check-mode compliance)

