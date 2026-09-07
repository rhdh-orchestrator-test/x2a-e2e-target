# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 6 custom modules implementing a multi-tier application stack architecture. The migration involves converting Puppet profiles, roles, and Hiera data to Ansible playbooks, roles, and variables. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB queries, custom functions, and multi-level Hiera hierarchy.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with custom Puppet functions and Bolt tasks
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: MOTD template management, utility package arrays, custom defined types (config_entry, create_dir), Bolt health check tasks, custom Facter facts

**profile_app_stack**:
- Description: Python application stack orchestrator with strict dependency chains, database connectivity, systemd service management, and monitoring integration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Custom database URL function, environment file templating, systemd service configuration, log rotation, health check scripts, Gunicorn worker management

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, service discovery, firewall integration, and comprehensive statistics
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration, SSL certificate management, custom error pages, stats interface, PuppetDB-based service discovery, firewall rule automation

**profile_postgresql**:
- Description: PostgreSQL database server installation and configuration with repository management and service orchestration
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: Version-specific package management, repository configuration, service dependency chains

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery, memory management, and authentication
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, memory policy configuration, password authentication, custom Facter facts for role detection

**role**:
- Description: Role definitions orchestrating profile combinations for different node types (app servers, load balancers, Redis clusters)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based node classification, profile dependency management, OS-specific execution paths

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge (stdlib, concat, firewall, vcsrepo, redis, systemd, apt)
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (node-specific, OS family, environment, common) for configuration data
- `manifests/site.pp`: Main site manifest for node classification and global configuration
- `data/`: Hiera data directory with environment-specific and common configuration values
- `Vagrantfile`: Development environment provisioning for testing
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (based on metadata.json operatingsystem_support)
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template and assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and apt modules

### Security Considerations

- **Hiera encrypted data**: Database passwords, Redis authentication, HAProxy stats credentials, and application secret keys are stored in plain text in Hiera YAML files - migrate to Ansible Vault
- **SSL certificate management**: HAProxy SSL configuration references certificate paths that need secure deployment via Ansible Vault or external certificate management
- **Service credentials**: Application database credentials and Redis passwords require vault encryption during migration
- **SSH hardening**: Current SSH configuration (permit_root_login: false, client_alive_interval) needs translation to Ansible ssh hardening roles
- **Firewall rules**: HAProxy firewall integration requires careful migration to ensure security policies are maintained

### Technical Challenges

- **PuppetDB queries**: profile_redis_cluster uses PuppetDB queries for cluster member discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet functions**: profile_app_stack::app_db_url function needs conversion to Jinja2 template or Ansible filter plugin
- **Hiera hierarchy complexity**: 4-level hierarchy (node/OS/environment/common) requires careful variable precedence mapping in Ansible
- **Strict dependency chains**: profile_app_stack enforces strict ordering (python -> database -> app -> service -> monitoring) - implement with Ansible handlers and task dependencies
- **Template complexity**: HAProxy configuration template with conditional SSL blocks and dynamic backend iteration needs Jinja2 conversion
- **Custom facts**: Facter plugins (haproxy_version.rb, redis_role.rb, base_utils_info.rb) require conversion to Ansible custom facts or setup module extensions

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and MOTD management with minimal dependencies
2. **profile_postgresql** (moderate complexity) - Database foundation required by application stack
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB query replacement and cluster logic
4. **profile_app_stack** (high complexity) - Complex dependency chain and custom functions
5. **profile_haproxy** (highest complexity) - Service discovery, SSL management, and firewall integration
6. **role** (final integration) - Role orchestration after all profiles are migrated

### Assumptions

- PuppetDB service discovery can be replaced with Ansible inventory-based approaches or external service discovery tools
- Custom Puppet functions can be adequately replaced with Jinja2 templates or Ansible filter plugins
- Hiera's 4-level hierarchy can be mapped to Ansible's variable precedence without functionality loss
- SSL certificate deployment process exists outside of Puppet and can be integrated with Ansible Vault
- Current firewall rules are documented and can be replicated in Ansible firewall modules
- Development and testing environments use the same OS distributions as production (RHEL 8/9, Debian 11/12, Ubuntu 22.04/24.04)
- Bolt task functionality (health checks, rolling restarts) can be replaced with Ansible ad-hoc commands or playbooks
- Service discovery requirements can be met without PuppetDB dependency through inventory management or external tools