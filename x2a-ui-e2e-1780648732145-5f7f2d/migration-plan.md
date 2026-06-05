# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the Apache web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with testinfra for Python-based testing
  - Option 2: Ansible Molecule with Goss for YAML-based testing
  - Option 3: Maintain InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles for:
  - Option 1: Deploy alternative compliance solutions like Ansible Automation Platform
  - Option 2: Create Ansible playbooks to deploy Chef products if they must be maintained

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security in the Apache configuration

- **SSH Security**: The SSH root login compliance check must be preserved
  - Convert the InSpec control to equivalent Ansible assertion or Molecule test
  - Maintain compliance metadata (STIG IDs, CCI references) in documentation

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting Ruby-based InSpec tests to an Ansible-compatible testing framework
  - Challenge: Preserving the same level of assertion capabilities and readability
  - Mitigation: Use testinfra with Python for complex assertions or Goss for simpler YAML-based tests

- **Compliance Metadata**: Preserving compliance metadata and references in the new testing framework
  - Challenge: InSpec has built-in support for compliance metadata that may not exist in other frameworks
  - Mitigation: Document compliance metadata in comments or separate documentation files

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: Ensuring idempotent installation and configuration
  - Mitigation: Use Ansible's package and service modules with appropriate state checks

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already Ansible, minimal changes needed)
2. **website_https_verify.rb** (convert InSpec test to Ansible-compatible test)
3. **ssh_profile.rb** (convert InSpec compliance control to Ansible-compatible test)
4. **chef-server-deployment** and **chef-automate-deployment** (convert bash scripts to Ansible playbooks)

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) can be used as-is with minimal modifications
2. The compliance testing provided by InSpec is still required in the Ansible-only solution
3. The deployment of Chef Automate/Server is still needed (if not, these components can be omitted from migration)
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates approach is acceptable for the migrated solution
6. No external dependencies or integrations beyond what's visible in the repository
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives