# MIGRATION FROM ANSIBLE WITH CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on maintaining the existing Ansible playbooks while replacing Chef InSpec with Ansible's native testing capabilities. The estimated timeline for this migration is 1-2 weeks, with low complexity as most of the infrastructure is already Ansible-based.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities (POODLE) by disabling older SSL protocols and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality and security
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For simple tests: Use Ansible assertions and the `assert` module
  - For more complex tests: Use Molecule for testing Ansible roles
  - For compliance testing: Consider migrating to Ansible's built-in `ansible-lint` or OpenSCAP integration

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure the SSL protocol restrictions are preserved (TLSv1.2 only)
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security tests in ssh_profile.rb need to be implemented in Ansible
  - Ensure PermitRootLogin is properly configured
  - Maintain compliance with security requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing framework
  - Challenge: InSpec has specific testing capabilities for SSL/TLS that may not have direct equivalents in Ansible
  - Mitigation: Use Ansible's `uri` module with appropriate SSL parameters and assertions

- **Chef Automate/Server Deployment**: Converting bash scripts to Ansible playbooks
  - Challenge: The Chef deployment scripts have specific ordering and dependencies
  - Mitigation: Create a dedicated Ansible role for Chef deployment with proper task ordering

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - No migration needed, but should be reviewed and potentially refactored into roles
   - Update testing framework from InSpec to Ansible native testing

2. **poodle_fix.yml** (low risk, already Ansible)
   - No migration needed, but should be reviewed for best practices
   - Update testing framework from InSpec to Ansible native testing

3. **Chef deployment scripts** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks are functioning correctly and don't require significant changes
2. The Chef InSpec tests are used primarily for validation and can be replaced with Ansible's testing capabilities
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment and not part of the core infrastructure
4. No external dependencies or modules are required beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The migration will maintain the same functionality and security posture as the original implementation