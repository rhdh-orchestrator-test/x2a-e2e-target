# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec testing capabilities within an Ansible-only workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website configuration
- `chef-and-ansible/index.html`: Likely a sample file for the website (content not examined)

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (referenced in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible_inspec` module or similar approach

### Security Considerations

- **SSL/TLS Configuration**: The playbooks handle SSL certificate generation and configuration. Migration should maintain or enhance these security practices.
- **POODLE Vulnerability Mitigation**: The poodle_fix.yml playbook specifically addresses SSL security. This should be preserved in the migration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook; consider using Ansible Vault for storing pre-generated certificates or private keys

### Technical Challenges

- **Chef Automate Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate's functionality (AWX/Tower or alternative)
- **InSpec Integration**: Ensuring continued compliance testing with InSpec while removing Chef dependencies
- **Configuration Parity**: Ensuring that the Ansible-based deployment provides the same level of configuration as the Chef-based approach

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need minor updates for best practices
2. **InSpec Tests**: Moderate complexity, need to integrate with Ansible-only workflow
3. **Chef Deployment Scripts**: High complexity, requires complete rewrite as Ansible playbooks

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content.
2. The Chef Automate and Chef Infra Server deployment scripts are intended to be run on a fresh Ubuntu system.
3. The existing Ansible playbooks are designed to work with Test Kitchen for testing purposes.
4. The InSpec tests are intended to verify the configuration applied by the Ansible playbooks.
5. The repository does not contain actual Chef cookbooks or recipes beyond the deployment scripts.
6. The hardcoded credentials in the deployment scripts are example values not used in production.
7. The migration goal is to eliminate Chef dependencies while maintaining the same functionality.