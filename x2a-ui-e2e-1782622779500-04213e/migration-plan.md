# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.
**Complexity**: Low to Medium - The existing Ansible playbooks can be retained with minimal changes, while the InSpec tests need to be converted to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server configuration and content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing configuration.
- `index.html`: Simple HTML file used for testing web server deployment. Can be retained as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that either:
  - Install and configure alternative tools like AWX/Ansible Tower
  - Or maintain Chef Automate/Server installation if still required, but managed via Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migration.
  
- **SSH Hardening**: The InSpec test validates SSH root login is disabled. This check should be converted to an Ansible-compatible test.

- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider enhancing this with Let's Encrypt integration for production environments.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test logic.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  
- **Test Kitchen to Molecule**: The testing workflow will need to be adjusted for Molecule's approach.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen configuration

- **Chef Server Deployment**: If Chef Server is still needed in the environment, its deployment and configuration will need to be carefully converted to Ansible.
  - Mitigation: Consider using the official Chef Ansible Collection if Chef Server must be maintained

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, can be retained with minimal changes
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions
3. **Test Kitchen Configuration**: Replace with Molecule configuration
4. **Chef Deployment Scripts**: Convert to Ansible playbooks for infrastructure management

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and can be retained with minimal changes.
2. The primary goal is to eliminate Chef InSpec dependencies while maintaining the same level of compliance testing.
3. The Chef Automate and Chef Server deployment scripts are intended to be replaced with Ansible equivalents, not maintained as-is.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the final implementation.
6. The self-signed certificates in the web server configuration are acceptable for the use case, or will be replaced with proper certificates in production.