# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 8 custom modules implementing a multi-tier web application stack. The migration involves converting Puppet profiles and roles to Ansible playbooks and roles, with particular attention to the complex Hiera hierarchy and PuppetDB-based service discovery. Estimated timeline: 6-8 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific Hiera data, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL backend, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, environment-specific configuration, logrotate integration, health check scripts

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, stats interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, SSL/TLS configuration, custom error pages, PuppetDB service discovery, backend configuration templates

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query integration, cluster node discovery, memory policy configuration, custom Facter facts

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing and development environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query functionality for non-production environments

**profile**:
- Description: Thin wrapper profiles that delegate to specific implementation modules (base, app, loadbalancer)
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Role composition layer, environment fact integration, delegation pattern

**role**:
- Description: Node classification roles combining base profiles with specific service profiles (app_stack, haproxy, redis_cluster)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Linux-specific exec path configuration, profile composition, dependency ordering

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge (stdlib, concat, firewall, vcsrepo, redis, systemd, apt)
- `environment.conf`: Module path configuration for Puppet environment
- `hiera.yaml`: 4-level hierarchy configuration (nodes, OS family, environment, common)
- `data/common.yaml`: Global configuration defaults with hardcoded passwords
- `data/environment/*.yaml`: Environment-specific overrides for production and staging
- `manifests/site.pp`: Main site manifest (likely node classification)
- `Vagrantfile`: Local development environment configuration
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9 and Ubuntu 24.04 LTS (based on metadata.json operatingsystem_support)
- **Virtual Machine Technology**: Not specified (Vagrant suggests VirtualBox for development)
- **Cloud Platform**: Not specified (no cloud-specific configurations detected)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template assembly or blockinfile module
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or iptables modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and apt modules

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in data/common.yaml:
  - HAProxy stats password: "test-haproxy-password"
  - Database password: "test-db-password" 
  - Redis password: "test-redis-password"
  - Application secret key: "test-secret-key"
- **SSL/TLS Configuration**: HAProxy module includes SSL certificate management requiring secure certificate deployment
- **Firewall Management**: Profile_haproxy includes firewall rules that need translation to Ansible firewall modules
- **Service Discovery**: PuppetDB queries for Redis cluster discovery need replacement with Ansible inventory or service discovery mechanism
- **Vault Integration**: Migrate to Ansible Vault for secrets management across all modules

### Technical Challenges

- **Complex Hiera Hierarchy**: 21-level hierarchy in profile_haproxy requires careful translation to Ansible variable precedence
- **PuppetDB Dependencies**: Redis cluster module uses PuppetDB queries for node discovery - needs replacement with Ansible inventory groups or external service discovery
- **Custom Puppet Functions**: profile_app_stack::app_db_url function needs conversion to Ansible Jinja2 filter or lookup plugin
- **Strict Dependency Chains**: profile_app_stack enforces strict ordering (python -> database -> app -> service -> monitoring) requiring careful Ansible handler and dependency management
- **Cross-Platform Support**: base_utils supports RedHat, Debian, and Ubuntu with OS-specific package lists requiring Ansible when/vars_files conditionals
- **Template Complexity**: HAProxy configuration template includes conditional SSL blocks and backend iteration requiring Ansible template conversion

### Migration Order

1. **base_utils** (low risk, foundational): Simple utility installation and MOTD management, no external dependencies
2. **profile_postgresql** (moderate complexity): Straightforward database installation with repository management
3. **profile** and **role** (low complexity): Thin wrapper classes easily converted to Ansible role composition
4. **profile_app_stack** (high complexity): Complex application deployment with custom functions and strict dependencies
5. **profile_haproxy** (high complexity): Complex load balancer with SSL, service discovery, and firewall integration
6. **profile_redis_cluster** (highest complexity): PuppetDB integration and cluster discovery requiring architectural changes

### Assumptions

- Test environment passwords in data/common.yaml will be replaced with Ansible Vault encrypted variables in production
- PuppetDB service discovery can be replaced with Ansible inventory groups or external service discovery tools
- SSL certificates referenced in HAProxy configuration are managed externally and will be deployed via Ansible certificate management
- The 21-level Hiera hierarchy in profile_haproxy can be simplified using Ansible's variable precedence without losing functionality
- Custom Puppet functions (ensure_value, normalize_port, app_db_url) can be replaced with equivalent Jinja2 filters or lookup plugins
- Bolt tasks for health checks and rolling restarts can be converted to Ansible ad-hoc commands or playbooks
- The strict dependency ordering in profile_app_stack is essential and must be preserved in Ansible handlers and task dependencies
- Container-based testing infrastructure can be adapted to use Ansible molecule for testing converted roles
- Environment-specific configuration (production.yaml, staging.yaml) patterns will be maintained using Ansible inventory group_vars