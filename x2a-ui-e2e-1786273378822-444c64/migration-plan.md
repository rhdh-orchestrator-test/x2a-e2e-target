# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing
- **Chef InSpec**: Convert InSpec tests to Ansible-native testing with:
  - ansible-lint for static analysis
  - testinfra for infrastructure testing
  - ansible-test for module testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Convert to Ansible role with proper templates for SSL configuration
  
- **SSH Hardening**: The SSH security profile tests must be maintained
  - Approach: Convert InSpec SSH tests to equivalent Ansible assertions or testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible/testinfra tests
  - Mitigation: Create a mapping of InSpec resources to testinfra methods
  - Example: InSpec's `describe port(443)` becomes testinfra's `host.socket("tcp://0.0.0.0:443")`

- **Chef Automate/Server Setup**: Replacing Chef server deployment scripts with Ansible
  - Mitigation: Create Ansible roles for Chef server deployment or consider migrating to pure Ansible without Chef server

### Migration Order

1. **website_https.yml** (Priority 1): Convert to Ansible role with proper structure
   - Create templates for Apache configuration
   - Move SSL certificate generation to separate tasks
   - Implement proper variable management

2. **poodle_fix.yml** (Priority 2): Integrate into the website role or create a separate security role
   - Ensure SSL hardening is maintained
   - Implement idempotent configuration

3. **InSpec Tests** (Priority 3): Convert to testinfra or other Ansible-compatible testing framework
   - Maintain the same level of compliance checking
   - Integrate with CI/CD pipeline

4. **Chef Server Scripts** (Priority 4): Evaluate if Chef server is still needed or can be replaced entirely with Ansible
   - If needed, create Ansible playbooks to deploy Chef infrastructure
   - If not needed, document migration path for existing Chef-managed nodes

### Assumptions

1. The current Ansible playbooks are functional but not following best practices for structure and organization
2. Chef InSpec is being used primarily for compliance testing, not for configuration management
3. The Chef Automate/Server setup scripts are used for infrastructure that may be replaced or migrated
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. There are no external dependencies or integrations not visible in the repository
6. The migration will maintain the same functionality while improving structure and maintainability