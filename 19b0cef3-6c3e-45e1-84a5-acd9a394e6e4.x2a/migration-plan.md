# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two lightweight cookbooks (nginx web server and Redis cache) to Ansible playbooks. This is a low-complexity migration with minimal dependencies and straightforward service management patterns.

**Estimated Timeline**: 1-2 weeks for a single developer
**Complexity Level**: Low - Basic package installation and service management only

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic nginx web server installation with service management and simple static content deployment
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, basic HTML file creation, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert to Ansible role with redis package management and service configuration

### Security Considerations

- **File Permissions**: Static HTML file created with explicit 0644 permissions and root ownership - maintain same security posture in Ansible
- **Service Management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **Vault/secrets management**: No secrets or credentials detected in the reviewed files - this is a basic installation without authentication or SSL configuration

### Technical Challenges

- **External Dependency Resolution**: The root cookbook depends on an external 'nginx' cookbook that is not present in the repository. Migration will need to either:
  - Include nginx configuration directly in the Ansible playbook
  - Use community nginx roles from Ansible Galaxy
  - Create custom nginx role based on the expected functionality
- **Attribute Translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults
- **Service Dependencies**: Ensure proper ordering between package installation and service management in Ansible tasks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity due to external dependency) - Create nginx playbook with integrated configuration or external role dependency

### Assumptions

- The external 'nginx' cookbook dependency provides standard nginx installation and configuration capabilities that can be replicated with community Ansible roles
- The target environment has package managers (apt/yum) available for nginx and redis-server packages
- No custom nginx configuration files or advanced features are required beyond basic installation
- Redis configuration can remain at default settings without custom redis.conf modifications
- The metadata-only dependency strategy mentioned in documentation is for testing purposes and doesn't indicate complex dependency management requirements in production
- Platform support (Ubuntu 18.04+, CentOS 7+) requirements will be maintained in the Ansible implementation
- No SSL/TLS configuration, authentication, or advanced security features are required for this basic setup