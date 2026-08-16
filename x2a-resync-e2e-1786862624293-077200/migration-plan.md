# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

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

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used for testing web server configuration. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for simpler testing
  - Option 3: Maintain InSpec as a standalone testing tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for automation platform
  - Ansible Content Collections for configuration management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration approach: Use Ansible's `openssl_*` modules (already in use) with proper certificate management.

- **SSH Security**: InSpec tests verify SSH root login is disabled. Migration approach: Create Ansible role that applies the same security configuration and use Ansible Molecule with Testinfra to verify compliance.

- **Vault/secrets management**: 
  - Hardcoded credentials in the Chef Automate deployment scripts (username, password). Migration approach: Replace with Ansible Vault for secure credential storage.
  - Self-signed certificates generated in the playbook. Migration approach: Use Ansible Vault to store sensitive key material or integrate with external certificate management.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible-compatible testing frameworks may require learning new testing approaches. Mitigation: Use Molecule with Testinfra which has similar capabilities to InSpec.

- **Chef Automate Functionality**: Replacing Chef Automate's compliance and reporting features with Ansible equivalents. Mitigation: Evaluate AWX/Ansible Tower reporting capabilities or integrate with additional tools like Prometheus/Grafana for monitoring and compliance reporting.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format. Refactor to follow Ansible best practices and role-based structure.

2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Moderate complexity, convert to Ansible Molecule with Testinfra or Goss.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef Automate/Infra Server functionality with Ansible equivalents.

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes, not production deployment, based on the README indicating it's related to content created by Technical Product Marketing.

2. The Chef InSpec tests are used for compliance validation of infrastructure configured by Ansible, suggesting a hybrid approach where Chef is used for testing and Ansible for configuration.

3. There are no external dependencies or integrations beyond what's visible in the repository.

4. The deployment scripts for Chef Automate and Chef Infra Server are intended for on-premises or generic cloud VM deployment, not specific to any cloud provider.

5. The security configurations (SSL, SSH) are basic examples and may need enhancement for production use.

6. The migration will maintain the same functionality but consolidate on Ansible as the single automation tool.