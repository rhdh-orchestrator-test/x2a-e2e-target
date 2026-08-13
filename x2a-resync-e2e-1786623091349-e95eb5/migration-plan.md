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
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing
- **Chef InSpec**: Convert InSpec tests to Ansible-native testing with:
  - ansible-lint for static analysis
  - testinfra for infrastructure testing
  - ansible-test for module testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to Ansible role with proper templates for SSL configuration
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled
  - Approach: Create Ansible role for SSH hardening that implements the same controls
  - Add ansible-lint rules to enforce SSH security best practices

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible/testinfra tests
  - Mitigation: Create a mapping between InSpec resources and testinfra modules
  - Example: InSpec's `describe port(443)` becomes testinfra's `host.socket("tcp://0.0.0.0:443")`

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure setup scripts with Ansible
  - Mitigation: Create Ansible roles for Chef server deployment or consider migrating to alternative solutions like AWX/Tower

### Migration Order

1. **website_https.yml** (Priority 1): Convert to Ansible role with proper structure
   - Create templates for Apache configuration
   - Move SSL certificate generation to separate tasks
   - Implement idempotent handlers

2. **poodle_fix.yml** (Priority 1): Integrate into a security hardening role
   - Create templates for SSL configuration
   - Add additional security hardening tasks

3. **InSpec Tests** (Priority 2): Convert to testinfra or other Ansible-compatible testing framework
   - Create equivalent tests for HTTPS configuration
   - Create equivalent tests for SSH hardening

4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles or evaluate alternatives
   - Create roles for Chef server deployment if still needed
   - Consider migrating to AWX/Tower instead of Chef Automate

### Assumptions

1. The current Ansible playbooks are functional but need restructuring to follow Ansible best practices
2. The Chef InSpec tests are used for compliance validation and need to be preserved in some form
3. The Chef Automate/Server deployment scripts may be optional for migration if the infrastructure is moving away from Chef
4. No complex Chef cookbooks or recipes are present that would require significant conversion effort
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The migration will maintain the same security posture and compliance requirements
7. No external dependencies or integrations beyond what's visible in the repository