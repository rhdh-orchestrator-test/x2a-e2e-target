# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching infrastructure. The migration is relatively straightforward due to the simple nature of the cookbooks, with an estimated timeline of 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic HTML content serving and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, basic HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management
- **cache (local)**: Convert to Ansible role dependency in requirements.yml or include as part of the same playbook

### Security Considerations

- **File permissions**: The cookbook creates /var/www/html/index.html with explicit mode 0644 and root ownership - ensure Ansible file module maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify proper systemd service configuration in target environment
- **No secrets detected**: This simple cookbook does not contain encrypted data bags, vault usage, or hardcoded credentials

### Technical Challenges

- **External dependency resolution**: The nginx cookbook dependency is declared in metadata but not resolvable without Berksfile/Policyfile - will need to identify appropriate Ansible nginx role or create custom tasks
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and startup sequence

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible tasks
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, configuration, and HTML file deployment, resolve external nginx dependency

### Assumptions

- The external nginx cookbook dependency will need to be replaced with either a community Ansible role or custom tasks, as no Berksfile/Policyfile exists to define the specific nginx cookbook version or source
- Target systems will have package managers (apt/yum) available for nginx and redis-server packages
- The simple HTML content approach suggests this is a basic web server setup rather than a complex application deployment
- Platform support is limited to Ubuntu 18.04+ and CentOS 7+ based on metadata declarations
- No complex nginx configuration is required beyond basic service setup, as evidenced by the minimal attribute set
- The metadata-only dependency strategy mentioned in documentation suggests this is a test/example repository rather than production infrastructure