# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate/Infra Server deployment scripts to Ansible

The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The repository appears to be primarily educational/demonstration in nature rather than a production infrastructure codebase.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL vulnerabilities in Apache by enforcing TLSv1.2
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
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH root login security compliance
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/index.html`: Sample HTML file used for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **chef-automate CLI**: Replace with Ansible roles for configuration management
- **InSpec (2.x/3.x)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to ansible-test framework
  - Option 2: Use Molecule for testing Ansible roles
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enforces TLSv1.2
- **SSH Hardening**: The SSH root login restrictions must be preserved in the Ansible configuration
- **Self-signed Certificates**: The certificate generation process should be maintained or improved
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Consider migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods will require careful mapping of test assertions
- **Chef Server Deployment**: Creating an equivalent Ansible playbook to replace the Chef server deployment scripts will require understanding of Chef server architecture

### Migration Order

1. **website_https.yml** (already Ansible, low risk)
2. **poodle_fix.yml** (already Ansible, low risk)
3. **InSpec Tests** (moderate complexity, requires framework change)
4. **Chef Deployment Scripts** (higher complexity, requires architectural understanding)

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production use
2. The InSpec tests are intended to validate the configurations applied by the Ansible playbooks
3. The Chef server deployment scripts are independent of the Ansible playbooks and InSpec tests
4. No external Chef cookbooks or recipes are being used beyond what's visible in the repository
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. The migration goal is to consolidate everything to Ansible, including the testing framework
7. No CI/CD pipeline integration is currently in place that would need to be updated
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only