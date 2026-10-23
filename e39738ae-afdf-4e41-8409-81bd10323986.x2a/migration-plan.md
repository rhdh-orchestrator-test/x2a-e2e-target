# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with a sophisticated multi-tier application stack implementing roles, profiles, and component modules using modern Puppet 7 features. The codebase demonstrates enterprise-grade patterns including Hiera hierarchy (up to 21 levels in some modules), PuppetDB integration, Bolt orchestration, custom facts, and custom Puppet functions. Migration complexity is HIGH due to deep Hiera hierarchies, dynamic node discovery, encrypted secrets (PKCS7), and extensive use of advanced Puppet features like virtual resources, exported resources, and custom Ruby-based extensions.

**Estimated Timeline**: 6-8 weeks for full migration with testing
- Week 1-2: Base infrastructure and profiles
- Week 3-4: Application stack and HAProxy with dynamic discovery
- Week 5-6: Testing, secret migration, and validation
- Week 7-8: Documentation and knowledge transfer

## Module Migration Plan

This repository contains Puppet modules organized using the roles and profiles pattern that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Foundation utility module providing cross-platform helper functions, custom facts, defined types, and Bolt orchestration tasks. Includes OS-specific package management, custom Facter plugins for platform detection, reusable configuration entry management, and health check orchestration capabilities.
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Facter fact (base_utils_info) for utility package detection and uptime, custom Puppet functions (ensure_value, normalize_port), defined types for configuration file entry management, Bolt plans/tasks for distributed health checks, MOTD template with OS-aware package lists, module-level Hiera hierarchy for OS-specific data

**profile::base::base**:
- Description: Base operating system profile applied to all node types handling common system services including NTP time synchronization via chrony, rsyslog configuration, and integration with base_utils module for platform utilities.
- Path: site-modules/profile/manifests/base
- Technology: Puppet
- Key Features: Conditional management of NTP and syslog based on Hiera lookups, OS kernel detection for Linux-specific resources, integration point for base_utils module, serves as foundation for all role compositions

**profile_app_stack**:
- Description: Full-stack Python web application deployment with PostgreSQL database, systemd service management, and comprehensive logging. Implements strict dependency chain orchestration across Python runtime, database setup, application deployment via Git, systemd service configuration, and monitoring integration with virtual resources.
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git-based application deployment using vcsrepo module, Python virtualenv with pip dependency management, custom Puppet function (app_db_url) for PostgreSQL connection string construction with URL encoding, systemd service generation from EPP templates, database user/database provisioning with PostgreSQL-specific exec resources, alembic migration support, logrotate configuration, environment-specific virtual resources for prometheus exporters, scheduled database backups via cron, health check integration, module-level Hiera with environment-specific overrides

**profile::app::stack**:
- Description: Thin wrapper profile that delegates to profile_app_stack module, providing environment-aware indirection layer following roles/profiles pattern.
- Path: site-modules/profile/manifests/app
- Technology: Puppet
- Key Features: Environment fact integration, profile delegation pattern

**profile_haproxy**:
- Description: Enterprise HAProxy load balancer with multi-level Hiera hierarchy (21 levels), dynamic backend discovery via PuppetDB queries, SSL/TLS termination, statistics page, firewall integration, and datacenter-aware configuration. Supports both static backend configuration and dynamic node discovery patterns.
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy (per-node, per-role, per-cluster, application tier, team, business unit, lifecycle, environment, network zone, datacenter, region, country, CPU architecture, OS release, OS family, kernel, container detection, virtual/physical, common), dynamic backend server discovery using PuppetDB queries and exported resources, custom Facter fact (haproxy_version) for version detection, iterative backend configuration generation from deeply-merged Hiera hash, systemd service override for multi-config loading, firewall management supporting firewalld/ufw/none providers, SSL certificate and cipher configuration, custom error page deployment (408, 503), HAProxy stats page with authentication, stick-table configuration for session persistence, configuration validation before service restart, SELinux policy management, logrotate integration, module-level Puppetfile for isolated dependencies

**profile::loadbalancer::haproxy**:
- Description: Thin wrapper profile that delegates to profile_haproxy module with environment fact awareness.
- Path: site-modules/profile/manifests/loadbalancer
- Technology: Puppet
- Key Features: Profile delegation pattern, environment integration

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management for version pinning, supporting Debian/Ubuntu platforms with version-specific package installation.
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository integration for PostgreSQL Global Development Group (PGDG) packages, version-specific package installation (PostgreSQL 15 default), GPG key management for repository authentication, libpq-dev installation for client libraries, service lifecycle management

**profile::cache::redis (profile_redis_cluster)**:
- Description: Redis cluster deployment using puppet-redis module with PuppetDB-based node discovery for cluster membership, custom Facter fact for role detection (primary/replica), and template-driven configuration.
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: Integration with puppet-redis community module, PuppetDB query for cluster node discovery, custom Facter fact (redis_role) determining primary/replica status from config files, Redis configuration via ERB templates with maxmemory, appendonly, and authentication settings, module-level Puppetfile for dependency isolation

**role::app_server**:
- Description: Composite role combining base profile, HAProxy, application stack, and Redis cache for a full application server node.
- Path: site-modules/role/manifests
- Technology: Puppet
- Key Features: Multi-profile composition, role-level orchestration

**role::app_stack**:
- Description: Application stack node role (Python app + PostgreSQL) with base profile and strict dependency ordering.
- Path: site-modules/role/manifests
- Technology: Puppet
- Key Features: Exec path defaults for Linux, profile composition with explicit ordering

**role::haproxy**:
- Description: HAProxy load balancer node role combining base OS profile with HAProxy-specific configuration.
- Path: site-modules/role/manifests
- Technology: Puppet
- Key Features: Role-based composition, dependency ordering

**role::redis_cluster**:
- Description: Redis cluster node role with base profile and cache profile composition.
- Path: site-modules/role/manifests
- Technology: Puppet
- Key Features: Role pattern implementation, profile ordering

**puppetdb_query_stub**:
- Description: Development stub for PuppetDB query function that returns empty arrays when PuppetDB is unavailable, enabling local testing without PuppetDB infrastructure.
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet (Ruby function)
- Key Features: Mock PuppetDB query implementation, warning logging for missing PuppetDB

### Infrastructure Files

- `Puppetfile`: Control repository Puppetfile declaring Puppet Forge module dependencies (stdlib 9.7.0, concat 9.0.2, firewall 8.1.3, vcsrepo 6.1.0, redis 11.0.0, systemd 7.1.0, inifile 6.1.1, apt 9.4.0). Migration consideration: Map these to appropriate Ansible Galaxy collections/roles.

- `environment.conf`: Defines Puppet modulepath hierarchy `site-modules:modules:$basemodulepath`. Migration consideration: Ansible roles/ and collections/ directory structure will replace this.

- `hiera.yaml`: Environment-level 4-layer Hiera hierarchy (per-node → per-OS → per-environment → common). Migration consideration: Ansible group_vars, host_vars, and inventory structure with precedence understanding.

- `manifests/site.pp`: Node classifier implementing test environment with test_git_repo class for creating local Git repository and applying role::app_server role. Migration consideration: Ansible playbooks and inventory will replace node classification.

- `data/common.yaml`: Global configuration defaults including NTP servers, SSH settings, syslog configuration, and default values for all profiles with test environment credentials. Migration consideration: Ansible all.yml group_vars with proper secret management.

- `data/environment/{production,staging}.yaml`: Environment-specific overrides for production infrastructure (internal NTP/syslog servers, worker counts, log levels, encrypted secrets). Migration consideration: Environment-specific group_vars with Ansible Vault.

- `site-modules/*/hiera.yaml`: Module-level Hiera configurations with varying hierarchy depths (base_utils: 3 levels, profile_haproxy: 21 levels, profile_app_stack: 2 levels). Migration consideration: Ansible role defaults and variable precedence will need careful mapping.

- `site-modules/*/data/`: Module-specific Hiera data directories containing OS-specific, environment-specific, datacenter-specific, and cluster-specific configuration data demonstrating complex hierarchical data merging. Migration consideration: Ansible role vars/ directories with strategic use of combine filter for hash merging.

- `site-modules/*/metadata.json`: Module metadata files declaring dependencies, supported OS versions (RHEL 8/9, Debian 11/12, Ubuntu 22.04/24.04), and Puppet version requirements (7.x-8.x). Migration consideration: Ansible role meta/main.yml with dependencies and platform specifications.

- `site-modules/base_utils/lib/facter/*.rb`: Custom Facter facts written in Ruby for platform detection and utility package verification. Migration consideration: Ansible custom facts or module execution for dynamic inventory/group assignment.

- `site-modules/*/lib/puppet/functions/*.rb`: Custom Puppet functions in Ruby for database URL construction and PuppetDB query stubbing. Migration consideration: Ansible custom filters or lookup plugins.

- `site-modules/base_utils/plans/*.pp`: Bolt orchestration plans for distributed health checks across node fleets. Migration consideration: Ansible ad-hoc commands or orchestration playbooks.

- `site-modules/base_utils/tasks/*`: Bolt task definitions (JSON + shell script) for service health verification. Migration consideration: Ansible modules or script execution.

- `site-modules/*/templates/*.{erb,epp}`: ERB and EPP templates for configuration files (MOTD, systemd units, HAProxy config, application environment files, logrotate). Migration consideration: Jinja2 templates with similar variable interpolation.

- `site-modules/*/files/*`: Static file sources (health check scripts, backup scripts, HAProxy error pages). Migration consideration: Ansible files/ directory with copy/template module usage.

- `Vagrantfile`: Development environment configuration for local testing. Migration consideration: Update for Ansible provisioner testing.

- `vagrant-provision.sh`: Shell script for Vagrant provisioning setup. Migration consideration: Replace with Ansible playbook execution.

- `test/`: Testing infrastructure with Containerfile and run script. Migration consideration: Update for Ansible testing with molecule or ansible-test.

### Target Details

Based on the repository metadata and configuration files:

- **Operating System**: Red Hat Enterprise Linux 8/9 (primary), Ubuntu 22.04/24.04, Debian 11/12. Inferred from metadata.json operatingsystem_support declarations across all modules, Hiera OS-specific data directories (RedHat.yaml, Debian.yaml), and package manager detection (yum/dnf vs apt). Default target: Red Hat Enterprise Linux 9.

- **Virtual Machine Technology**: Not explicitly specified. File paths suggest standard Linux environments without VM-specific tooling references. Infrastructure appears cloud/VM-agnostic.

- **Cloud Platform**: Not specified. Configuration shows internal datacenter references (dc1_fra, internal DNS names like db-primary.prod.internal, ntp1.prod.internal) suggesting on-premises or private cloud deployment. No AWS/Azure/GCP-specific resources detected.

## Migration Approach

### Key Dependencies to Address

External Puppet Forge module dependencies requiring Ansible equivalents:

- **puppetlabs-stdlib (9.7.0)**: Core Puppet functions and types for data validation and manipulation. Replace with Ansible built-in filters, validation modules, and community.general collection utilities.

- **puppetlabs-concat (9.0.2)**: File fragment concatenation used for building composite configuration files. Replace with Ansible template module with blockinfile or assemble module for fragment-based configs, or Jinja2 template logic for iterative content generation.

- **puppetlabs-firewall (8.1.3)**: Cross-platform firewall resource management. Replace with ansible.posix.firewalld module for RHEL or community.general.ufw for Ubuntu, with conditional task execution based on OS family.

- **puppetlabs-vcsrepo (6.1.0)**: Git repository management for application deployment. Replace with ansible.builtin.git module with equivalent version pinning and update strategies.

- **puppet-redis (11.0.0)**: Redis installation and configuration management. Replace with community.general.redis or geerlingguy.redis Ansible role with equivalent configuration templating.

- **puppet-systemd (7.1.0)**: Systemd unit management and daemon reloading. Replace with ansible.builtin.systemd module with daemon_reload and service management capabilities.

- **puppetlabs-inifile (6.1.1)**: INI file key/value manipulation. Replace with community.general.ini_file module for direct INI manipulation.

- **puppetlabs-apt (9.4.0)**: APT repository and package management. Replace with ansible.builtin.apt_repository and ansible.builtin.apt modules with equivalent GPG key handling.

### Security Considerations

The repository contains multiple security configurations requiring careful migration attention:

- **Encrypted Secrets (PKCS7)**: Hiera data files contain PKCS7-encrypted values (identified by `ENC[PKCS7,...]` prefix) for database passwords, HAProxy stats authentication, application secret keys, and production credentials. These appear in:
  - `profile_app_stack::db_password` - Database credentials
  - `profile_app_stack::secret_key` - Application secret keys (production)
  - `profile_haproxy::stats_password` - HAProxy statistics page authentication
  - Migration approach: Re-encrypt all secrets using Ansible Vault (ansible-vault encrypt_string), organize in separate vault files per environment (vault_production.yml, vault_staging.yml), implement vault password management strategy (vault password files or integration with secret management systems like HashiCorp Vault)

- **Credential Distribution**: Secrets are distributed throughout Hiera hierarchy levels (common, environment, datacenter, node-specific). Count of encrypted credentials per module:
  - profile_app_stack: 2-3 encrypted values (db_password, secret_key)
  - profile_haproxy: 1 encrypted value (stats_password)
  - profile_redis_cluster: 1 plaintext password requiring encryption (redis_password)
  - Migration approach: Consolidate vault structure with clear environment/module separation, implement vault_id labels for multi-environment management

- **SSL/TLS Configuration**: HAProxy SSL configuration references certificate and key paths (`ssl_cert_path: /etc/ssl/certs`, `ssl_key_path: /etc/ssl/private`) with cipher specifications and minimum TLS version (TLSv1.2). Migration approach: Use Ansible certificate modules (community.crypto collection) for certificate deployment, implement certificate renewal automation if using Let's Encrypt

- **SSH Hardening**: Global SSH configuration with hardened settings (permit_root_login: false, client_alive_interval: 300). Migration approach: Use ansible.builtin.lineinfile or community.general.ssh_config for SSH daemon hardening

- **Firewall Rules**: Multi-provider firewall management (firewalld for RHEL, ufw for Ubuntu) with conditional application. Migration approach: Use ansible.posix.firewalld and community.general.ufw modules with OS-conditional task execution

- **SELinux Policies**: HAProxy module includes optional SELinux boolean configuration for network connectivity. Migration approach: Use ansible.posix.seboolean module with appropriate policy settings

- **Database Security**: PostgreSQL user and database creation with privilege management using raw SQL execution. Migration approach: Use community.postgresql collection modules (postgresql_user, postgresql_db) with Ansible Vault for credentials

- **Service Account Management**: Application runs under dedicated service accounts (app_user, haproxy user) with specific shell and home directory restrictions (nologin shell, system accounts). Migration approach: Use ansible.builtin.user and ansible.builtin.group modules with equivalent security settings

### Technical Challenges

Complex patterns requiring special attention during migration:

- **21-Level Hiera Hierarchy**: The profile_haproxy module implements an exceptionally deep Hiera hierarchy spanning organizational (team, business_unit), infrastructure (datacenter, region, country, network_zone), technical (OS, architecture, virtual/physical), and deployment (environment, cluster, role, node) dimensions. This demonstrates advanced data separation and override patterns.
  - Challenge: Ansible's variable precedence system (22 levels) differs fundamentally from Hiera's hierarchy
  - Mitigation: Design Ansible inventory structure with strategic group nesting (datacenter → environment → role → host), use group_vars with numeric prefixes for precedence control, implement hash_behaviour=merge setting or explicit combine filter usage for deep merging, document variable precedence decisions clearly for team understanding

- **Deep Hash Merging**: The `profile_haproxy::backends` hash demonstrates deep merge behavior across multiple hierarchy levels (common defines default backend structure, datacenter level overrides server addresses, environment level adjusts timeouts/connections).
  - Challenge: Ansible's default behavior is to replace entire hashes rather than merge them
  - Mitigation: Use `combine(recursive=True)` filter explicitly in playbooks/roles, consider hash_behaviour=merge in ansible.cfg (though deprecated), implement explicit merge logic in role defaults and vars for critical configuration structures

- **PuppetDB Integration**: Both profile_haproxy::discover and profile_redis_cluster use PuppetDB queries for dynamic node discovery and cluster membership determination. The exported resource pattern (`@@haproxy::balancermember`) enables nodes to self-register as load balancer backends.
  - Challenge: Ansible has no direct equivalent to PuppetDB's centralized state database and exported resources
  - Mitigation: Replace with dynamic inventory scripts querying infrastructure inventory sources (CMDB, cloud provider APIs, Consul/etcd service discovery), use Ansible Tower/AWX for centralized facts caching, implement registration pattern using ansible.builtin.add_host for dynamic group population, consider Redis/etcd as shared state backend for distributed facts, use ansible.builtin.set_fact with delegate_to/run_once for cross-host data sharing

- **Custom Ruby Functions**: Three custom Puppet functions written in Ruby extend Puppet's DSL:
  - `profile_app_stack::app_db_url` - Constructs PostgreSQL connection URLs with proper encoding
  - `puppetdb_query` - Stub for PuppetDB queries in development
  - Base_utils functions (ensure_value, normalize_port) - Type validation and coercion
  - Challenge: Ruby functions require reimplementation in Python for Ansible
  - Mitigation: Convert to Ansible filter plugins (create filter_plugins/ directory), implement URL encoding filter using urllib.parse, normalize_port as type casting filter, test thoroughly as Python string handling differs from Ruby

- **Custom Facter Facts**: Three custom facts collect system state in Ruby:
  - `base_utils_info` - Detects installed utility packages and system uptime
  - `haproxy_version` - Extracts HAProxy version from command output
  - `redis_role` - Determines Redis primary/replica status from config files
  - Challenge: Ansible facts system differs from Facter's Ruby-based approach
  - Mitigation: Implement as custom fact modules in module_utils/, use ansible.builtin.setup with fact_path for external facts, consider whether facts are needed at all (could be replaced by direct command execution in playbooks), for version detection use ansible.builtin.package_facts or command output parsing

- **Virtual Resources**: profile_app_stack::monitoring uses virtual resources (`@package`, `@service`, `@cron`) that are declared but only realized in production environment, enabling DRY code with conditional application.
  - Challenge: Ansible has no direct virtual resource equivalent
  - Mitigation: Use conditional task execution with when: ansible_env.environment == 'production', implement tags for optional resource application (--tags monitoring), use include_tasks with conditional statements for environment-specific playbook segments

- **Bolt Orchestration**: base_utils module includes Bolt plans and tasks for distributed health check orchestration across node fleets.
  - Challenge: Bolt's orchestration model differs from Ansible's push-based execution
  - Mitigation: Convert Bolt plans to Ansible playbooks with serial execution control, replace Bolt tasks with ansible.builtin.script or ansible.builtin.command modules, use Ansible Tower/AWX workflow templates for complex orchestration scenarios, implement ansible.builtin.async for parallel task execution patterns

- **Strict Dependency Chains**: profile_app_stack implements explicit dependency ordering using chain arrows (`->` and `~>`), ensuring Python → Database → App → Service → Monitoring sequence.
  - Challenge: Ansible's declarative nature handles ordering differently than Puppet's DSL
  - Mitigation: Use pre_tasks and post_tasks for phase separation, implement handler notifications for service restarts, leverage role dependencies in meta/main.yml, structure playbook tasks in correct order (Ansible executes sequentially), use ansible.builtin.meta: flush_handlers at strategic points

- **Template Diversity**: The codebase uses both ERB (Ruby-based) and EPP (Puppet-native) template formats with different syntax and capabilities.
  - Challenge: All templates must convert to Jinja2 with different syntax
  - Mitigation: Create Jinja2 template equivalents testing thoroughly (ERB <%= var %> becomes {{ var }}, conditionals and loops map cleanly), validate rendered outputs against original Puppet-generated configs, maintain template test suite to catch rendering differences

- **Module-Level Puppetfiles**: Both profile_haproxy and profile_redis_cluster include their own Puppetfile declarations for isolated dependency management.
  - Challenge: Ansible doesn't support per-role requirements files natively
  - Mitigation: Consolidate all collection requirements in central requirements.yml, use collection namespacing to avoid conflicts, document role-specific collection dependencies in role meta/main.yml, consider Ansible collection development if tight coupling is required

- **Systemd Overrides**: profile_haproxy uses systemd drop-in files to modify service execution with multi-config loading.
  - Challenge: Managing systemd overrides requires file placement and daemon reloading
  - Mitigation: Use ansible.builtin.systemd module with daemon_reload parameter, template systemd override files to /etc/systemd/system/service.d/, implement handlers for daemon reload and service restart

- **Configuration Validation**: HAProxy module validates configuration syntax before applying service restarts using refreshonly exec resources.
  - Challenge: Ansible's default behavior doesn't include pre-restart validation
  - Mitigation: Implement validation tasks with ansible.builtin.command and register output, use failed_when to abort on validation errors, structure handlers to run validation before service restart, consider check_mode support for safe execution

### Migration Order

Recommended phased migration approach based on dependencies and complexity:

**Phase 1: Foundation (Week 1-2)**
1. **base_utils** - Low risk, no external dependencies beyond stdlib, provides reusable utilities for subsequent modules. Migrate custom functions to Ansible filters first.
2. **profile::base::base** - Simple OS-level services (chrony, rsyslog) with minimal complexity. Establishes base role pattern.
3. **profile_postgresql** - Straightforward repository and package management, needed as dependency for application stack.

**Phase 2: Core Services (Week 3-4)**
4. **profile_redis_cluster** - Moderate complexity with community module dependency and PuppetDB integration. Replace PuppetDB discovery with inventory-based approach.
5. **profile_app_stack** (without monitoring) - High complexity but critical business value. Migrate in sub-phases: Python → Database → App → Service. Leave virtual monitoring resources for Phase 3.
6. **profile::app::stack** - Thin wrapper, migrate after profile_app_stack core.

**Phase 3: Load Balancing & Advanced Features (Week 5-6)**
7. **profile_haproxy** (static configuration) - Begin with static backend configuration from Hiera, skip dynamic discovery initially. Address 21-level hierarchy with structured group_vars.
8. **profile_haproxy** (dynamic discovery) - Add PuppetDB replacement and exported resource patterns using dynamic inventory or shared state backend.
9. **profile::loadbalancer::haproxy** - Wrapper profile after main module.
10. **profile::cache::redis** - Wrapper profile completion.

**Phase 4: Roles & Orchestration (Week 7)**
11. **role::app_stack** - Compose migrated profiles into Ansible playbook.
12. **role::haproxy** - Load balancer role composition.
13. **role::redis_cluster** - Redis role composition.
14. **role::app_server** - Complex multi-profile role combining all components.
15. **puppetdb_query_stub** - May be unnecessary in Ansible context if replaced by inventory patterns.

**Phase 5: Advanced Features & Testing (Week 8)**
16. **profile_app_stack::monitoring** - Virtual resources and environment-conditional monitoring.
17. **Bolt plans/tasks** - Convert to Ansible orchestration playbooks with proper targeting.
18. Integration testing across all roles with production-like configurations.

**Rationale**: This order builds from simple base utilities upward through dependency layers, deferring complex features (PuppetDB integration, deep Hiera hierarchy, virtual resources) until foundational patterns are established. Each phase delivers working infrastructure that can be validated before proceeding.

### Assumptions

- **Hiera Hierarchy Necessity**: The 21-level Hiera hierarchy in profile_haproxy suggests a large, complex multi-datacenter enterprise environment. Assumption: The full hierarchy depth is actively used with meaningful overrides at multiple levels. If many levels are unused, the Ansible design can be simplified. Clarification needed: Which hierarchy levels contain actual overrides vs. theoretical structure?

- **PuppetDB Usage Patterns**: The codebase includes both real PuppetDB integration (profile_haproxy::discover, profile_redis_cluster) and stub implementations (puppetdb_query_stub). Assumption: PuppetDB is used in production for dynamic discovery. Clarification needed: Is PuppetDB actually deployed and used, or are static configurations sufficient? This significantly impacts the complexity of the Ansible migration.

- **Exported Resource Dependencies**: The HAProxy discovery module uses exported resources (`@@haproxy::balancermember`) implying multi-node coordination. Assumption: Puppet runs occur in a specific order allowing exported resources to be collected. Clarification needed: How are Puppet runs orchestrated to ensure proper resource export/collection timing? Ansible will need equivalent coordination mechanism.

- **Environment Fact Source**: Multiple profiles reference `$facts['environment']` and conditional logic based on environment detection. Assumption: The environment fact is set via external node classifier or custom fact script. Clarification needed: How is the environment fact populated (ENC, trusted facts, custom Facter script)? This determines the Ansible inventory structure and group assignment strategy.

- **PKCS7 Decryption**: Encrypted Hiera values use PKCS7 format suggesting hiera-eyaml or similar tooling. Assumption: Decryption keys are available for migration. Clarification needed: Are PKCS7 private keys available to decrypt secrets for re-encryption with Ansible Vault? Security procedures for key handling during migration?

- **Certificate Management**: HAProxy SSL configuration references certificate paths but doesn't show certificate provisioning. Assumption: Certificates are managed out-of-band (manual placement, separate automation, certbot). Clarification needed: How are SSL certificates currently deployed? Should certificate management be included in Ansible migration?

- **Database Provisioning Scope**: profile_app_stack creates PostgreSQL users and databases using raw SQL execution. Assumption: This is the only database automation required (no replication, backup/restore, performance tuning). Clarification needed: Are there additional database management tasks not visible in this module that need migration?

- **Redis Cluster Topology**: profile_redis_cluster uses PuppetDB to discover cluster nodes and includes a custom fact for primary/replica detection. Assumption: Redis cluster uses built-in replication, not Redis Cluster mode. Clarification needed: What is the actual Redis topology (standalone, replication, cluster mode, sentinel)? This affects the Ansible role design.

- **Firewall Provider Selection**: Firewall management supports three providers (firewalld, ufw, none) with Hiera-driven selection. Assumption: Each OS family uses one consistent provider (RHEL→firewalld, Ubuntu→ufw). Clarification needed: Are there mixed environments where the same OS might use different providers?

- **Bolt Usage Scope**: The repository includes Bolt plans and tasks for health checking. Assumption: Bolt is used for operational tasks, not initial provisioning. Clarification needed: What other Bolt orchestration exists beyond this repository? Are there dependencies on Bolt workflows that need replacement?

- **Virtual Resource Realization**: The monitoring class uses virtual resources realized only in production. Assumption: Environment-based realization is the only virtual resource pattern. Clarification needed: Are there other virtual resource patterns in use? What determines when resources should be virtual vs. concrete?

- **Test Environment Accuracy**: The test environment in site.pp creates a mock Git repository and uses test credentials. Assumption: This accurately represents production deployment patterns. Clarification needed: Do production deployments follow the same Git-based flow, or are there additional deployment steps (artifact repositories, CI/CD integration)?

- **Module Isolation**: Some modules include their own Puppetfile suggesting independent versioning. Assumption: Module versions can be locked independently. Clarification needed: Are the site-modules published to internal Forge, or is this a monorepo? Does Ansible migration need to maintain module independence?

- **OS Support Matrix**: Metadata declares support for RHEL 8/9, Debian 11/12, Ubuntu 22.04/24.04. Assumption: All OS versions receive equal testing and production usage. Clarification needed: What is the actual production OS distribution? Can the Ansible migration target a subset for initial rollout?

- **Custom Function Complexity**: Custom Puppet functions perform URL encoding and PuppetDB queries. Assumption: These are the only custom Ruby extensions requiring migration. Clarification needed: Are there additional Ruby extensions in libraries not visible in this repository snapshot?

- **Hiera Merge Behavior**: The profile_haproxy backends hash demonstrates deep merge with lookup_options. Assumption: Deep merge is configured globally in hiera.yaml. Clarification needed: What is the global Hiera merge strategy (first, unique, hash, deep)? This affects how Ansible variable merging should be configured.

- **Service Dependencies**: The application stack has strict ordering (python → database → app → service → monitoring). Assumption: This order is critical and failures should halt progression. Clarification needed: Are there acceptable partial-failure scenarios, or must all components deploy successfully?

- **Secret Rotation**: Encrypted passwords appear in multiple Hiera levels. Assumption: Secrets are rotated infrequently and can be manually re-encrypted during migration. Clarification needed: Is there automated secret rotation requiring integration with Ansible Vault?

- **Vagrant Usage**: The repository includes Vagrant configuration for local development. Assumption: Developers actively use Vagrant for testing. Clarification needed: Will Ansible migration need to maintain Vagrant compatibility for local development workflows?

- **Container Support**: Test infrastructure includes a Containerfile. Assumption: Containerized testing is part of the CI/CD pipeline. Clarification needed: Are Ansible roles expected to work in containerized environments? Does the migration need to support container-based testing?
