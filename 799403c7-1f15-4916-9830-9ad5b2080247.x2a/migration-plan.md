# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 7 custom modules implementing a complete application stack infrastructure. The migration involves converting Puppet manifests, Hiera data hierarchies, and ERB templates to Ansible playbooks, roles, and Jinja2 templates. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation across all nodes
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: MOTD template management, utility package installation, custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks and rolling restarts

**profile_app_stack**:
- Description: Complete Python application stack with Git deployment, virtual environment management, PostgreSQL database integration, and systemd service orchestration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository cloning via vcsrepo, Python virtualenv creation, pip requirements installation, Alembic database migrations, environment file templating, health check scripts

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, stats interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: SSL/TLS configuration, backend discovery via PuppetDB queries, stats dashboard, custom error pages, firewall rule management, 21-level Hiera hierarchy support

**profile_postgresql**:
- Description: PostgreSQL database server installation and configuration with repository management
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PostgreSQL 15 installation, repository configuration, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with node discovery and memory management
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB-based node discovery, memory policy configuration, cluster node coordination

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query functionality for development/testing

**role**:
- Description: Role definitions orchestrating profile classes for different server types (app_server, app_stack, haproxy, redis_cluster)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based node classification, profile composition, dependency ordering

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt
- `environment.conf`: Module path configuration for site-modules and external modules
- `hiera.yaml`: 4-level hierarchy (nodes, OS family, environment, common) with YAML backend
- `data/`: Hiera data files with environment-specific and common configuration
- `manifests/site.pp`: Main site manifest with node classification and test repository setup
- `Vagrantfile`: Development environment configuration
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9 (with Ubuntu 22.04/24.04 and Debian 11/12 support based on metadata)
- **Virtual Machine Technology**: Not specified (supports multiple platforms via Vagrant)
- **Cloud Platform**: Not specified (infrastructure-agnostic deployment)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin modules and community.general collection
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.service modules
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded credentials in Hiera data**: Database passwords, Redis passwords, HAProxy stats passwords, and application secret keys are stored in plain text in YAML files
  - profile_app_stack::db_password: "test-db-password"
  - profile_app_stack::secret_key: "test-secret-key"
  - profile_haproxy::stats_password: "test-haproxy-password"
  - profile_redis_cluster::redis_password: "test-redis-password"
- **SSL/TLS certificate management**: HAProxy SSL configuration references certificate paths that need secure deployment
- **Application environment files**: Database URLs and secrets templated into .env files with restricted permissions (0600)
- **SSH hardening configurations**: Root login disabled, client alive intervals configured
- **Service account management**: Application user/group creation and permission management

### Technical Challenges

- **PuppetDB query dependencies**: profile_redis_cluster and profile_haproxy use PuppetDB queries for node discovery - requires replacement with Ansible inventory or dynamic inventory scripts
- **Complex Hiera hierarchy**: 21-level hierarchy in profile_haproxy with node, cluster, datacenter, environment, and OS-specific data layers - needs careful variable precedence mapping in Ansible
- **Custom Puppet functions**: profile_app_stack::app_db_url function builds database connection strings - requires conversion to Jinja2 filters or custom Ansible modules
- **ERB template complexity**: HAProxy configuration template with conditional SSL blocks and backend iteration - needs Jinja2 conversion with equivalent logic
- **Strict dependency chains**: profile_app_stack enforces python -> database -> app -> service -> monitoring order using Puppet's contain/require - requires careful task ordering in Ansible
- **Bolt task integration**: health_check.pp and rolling_restart.pp tasks need conversion to Ansible ad-hoc commands or playbooks

### Migration Order

1. **base_utils** (low risk, foundational): MOTD management, package installation, utility functions - establishes baseline Ansible patterns
2. **profile_postgresql** (moderate complexity): Database server setup with repository management - enables application stack dependencies
3. **profile_app_stack** (high complexity): Python application deployment with Git, virtualenv, and database integration - core business logic
4. **profile_haproxy** (high complexity): Load balancer with SSL, backend discovery, and firewall integration - complex templating and networking
5. **profile_redis_cluster** (moderate complexity): Redis cluster with node discovery - requires inventory integration solutions
6. **role definitions** (low complexity): Role composition and node classification - orchestrates all profiles
7. **puppetdb_query_stub** (low complexity): Testing utilities - development/testing support

### Assumptions

- Test environment credentials are placeholders and will be replaced with proper secret management in production
- The Git repository referenced in profile_app_stack (/tmp/test-app-repo) is a test fixture and actual application repositories will be provided
- HAProxy backend discovery via PuppetDB can be replaced with static inventory or dynamic inventory solutions
- The 21-level Hiera hierarchy in profile_haproxy represents actual production complexity and all levels are actively used
- SSL certificates referenced in HAProxy configuration will be managed through separate certificate deployment processes
- The application stack supports standard Python deployment patterns (virtualenv, pip, Alembic migrations)
- Firewall management can be standardized across the infrastructure (currently set to "none" provider in test data)
- The Bolt tasks (health checks, rolling restarts) are actively used in production operations and need Ansible equivalents
- Container-based testing infrastructure in test/ directory represents current CI/CD patterns that should be preserved
- The profile/role pattern separation should be maintained in the Ansible migration for consistency with existing operational procedures