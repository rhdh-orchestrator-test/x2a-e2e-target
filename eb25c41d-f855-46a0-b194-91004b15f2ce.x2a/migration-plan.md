# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate basic web server and caching infrastructure. The migration is relatively straightforward due to the simple nature of the cookbooks, with an estimated timeline of 1-2 weeks for a small team. The main complexity lies in handling the external nginx dependency and ensuring proper service orchestration between the web server and cache components.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root directory)
- Technology: Chef
- Key Features: Package installation, service enablement, static file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook platform support declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation and configuration

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify proper service dependencies in Ansible playbooks
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency declared in metadata.rb needs to be resolved through Ansible Galaxy or custom role development
- **Service orchestration**: Ensure proper startup order between nginx and redis services in Ansible playbooks
- **Attribute translation**: Convert Chef attributes (nginx port, user, worker processes) to Ansible variables with appropriate defaults
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS platforms using Ansible conditionals

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency)

### Assumptions

- The external nginx dependency mentioned in metadata.rb will need to be replaced with a suitable Ansible role from Galaxy or custom development
- The target environment supports both Ubuntu and CentOS platforms as specified in the cookbook metadata
- No complex configuration templates or data bags are used beyond the simple attributes defined
- The metadata-only dependency strategy mentioned in README.md suggests this is a test/example repository rather than production infrastructure
- Service dependencies between nginx and redis are not explicitly defined and may need to be established in Ansible playbooks
- No custom Chef resources or complex cookbook patterns are used - migration should be straightforward resource-to-module translation