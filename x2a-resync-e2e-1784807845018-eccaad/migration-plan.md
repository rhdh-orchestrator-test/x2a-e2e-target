# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of Ansible playbooks for web server configuration and Chef InSpec tests for validation, along with Chef Automate/Infra Server setup scripts. The estimated timeline for migration is 1-2 weeks given the limited scope and straightforward configurations.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for validating HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Ansible using ansible_inspec module
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable vulnerable protocols. Migration should maintain or enhance this security posture.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider integrating with Let's Encrypt for production environments.
- **SSH Hardening**: InSpec tests validate SSH security configurations. Ensure these compliance checks are maintained in the Ansible migration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to equivalent Ansible assertions or maintaining InSpec as a separate validation tool
- **Test Kitchen to Molecule**: Adapting the testing workflow from Test Kitchen to Ansible Molecule
- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate's compliance and reporting features

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
2. **poodle-fix playbook** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible-compatible testing)
4. **Chef Automate/Server deployment scripts** (high complexity, requires architectural decisions)

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.
2. The InSpec tests are intended to validate both Ansible and Chef configurations, suggesting a hybrid approach to infrastructure management.
3. The Chef Automate and Chef Infra Server setup scripts are used for demonstration environments and contain non-production default values.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The migration will maintain the same level of security compliance validation currently provided by InSpec.
6. No complex data structures or external dependencies are used in the current implementation.
7. The migration will need to address the hardcoded credentials in the setup scripts.