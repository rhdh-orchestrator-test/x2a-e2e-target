# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

**Complexity**: Low to Medium - The existing Ansible playbooks can be preserved with minimal changes, while the InSpec tests need to be converted to Ansible's testing framework.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible Molecule for testing
- `index.html`: Sample HTML file used for testing - can be preserved as-is or incorporated into Ansible templates

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For simple tests: Use Ansible assert module within playbooks
  - For comprehensive testing: Implement Ansible Molecule with testinfra or ansible-test
  - For compliance testing: Consider migrating to OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migrated solution.
  - Migration approach: Preserve the existing Ansible tasks that configure SSL/TLS

- **SSH Security**: The InSpec tests validate SSH security configurations according to STIG standards.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated during deployment and don't require migration of existing secrets

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use Ansible's assert module for simple tests, and Molecule with testinfra for more complex validations

- **Compliance Validation**: Preserving compliance validation capabilities currently provided by InSpec
  - Mitigation: Consider implementing OpenSCAP with Ansible for compliance testing or use ansible-lint with custom rules

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible playbooks
  - Mitigation: Create new Ansible roles for Chef server deployment or consider if Chef server is still needed after migration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can be preserved with minimal changes
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks or evaluate if still needed

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes
2. The Chef InSpec tests are used primarily for validation and compliance checking, not for configuration management
3. The deployment scripts for Chef Automate and Chef Infra Server may not be needed after migration to Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. There are no external dependencies or integrations not visible in the provided repository
6. The migration is part of a broader strategy to standardize on Ansible and eliminate Chef dependencies
7. No custom InSpec resources or complex test patterns are used beyond what's visible in the provided tests