# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a standardized Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring web servers with HTTPS
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The main focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-based workflow.

Estimated timeline: 1-2 weeks for a complete migration, with minimal disruption to existing operations.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **compliance-testing**:
    - Description: Chef InSpec tests for verifying SSH security and HTTPS configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, HTTPS port and protocol verification

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `deploy-chef-server.sh`: Script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Integrate with Ansible using the `ansible.builtin.shell` module or migrate to Ansible-native solutions:
  - For SSH compliance: Use Ansible's `openssh_config` module
  - For HTTPS verification: Use Ansible's `uri` module with SSL verification

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables vulnerable protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Use Ansible's `lineinfile` or `template` modules to manage Apache SSL configuration

- **SSH Security**: Current InSpec tests verify that SSH root login is disabled.
  - Migration approach: Use Ansible's `openssh_config` module to enforce SSH security settings and verify compliance

- **Vault/secrets management**: 
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Integration**: The current setup uses InSpec for compliance testing.
  - Mitigation strategy: Either continue using InSpec with Ansible (using the `shell` module) or migrate to Ansible-native testing with `assert` and `uri` modules

- **Chef Server Replacement**: The deployment scripts set up Chef Server for configuration management.
  - Mitigation strategy: Replace with AWX/Ansible Tower or other Ansible control node setup

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible format)
2. **ssl-poodle-vulnerability-fix** (low risk, already in Ansible format)
3. **compliance-testing** (moderate complexity, requires adapting InSpec tests to Ansible)
4. **chef-automate-deployment** (high complexity, requires replacing Chef-specific functionality)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The Chef Automate and Chef Infra Server deployment is intended for testing/demonstration purposes.
3. There are no external dependencies or integrations not visible in the repository.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. There are no specific performance requirements for the migrated solution.
7. The InSpec tests are essential and must be preserved in some form in the migrated solution.