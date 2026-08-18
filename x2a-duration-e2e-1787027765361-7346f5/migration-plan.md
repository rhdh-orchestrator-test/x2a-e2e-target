# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec tests for compliance validation

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains a combination of Ansible playbooks, Chef InSpec tests, and Chef Automate/Infra Server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for validating HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test profile for validating SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for Chef Automate/Infra Server deployment or consider if Chef Automate is still needed
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing or maintain Test Kitchen if preferred
- **InSpec**: Maintain InSpec for compliance testing, as it works well with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migrated solution.
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be maintained.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **Chef Automate/Infra Server Deployment**: Converting the bash scripts to idempotent Ansible playbooks will require careful handling of the Chef Automate CLI commands and ensuring proper error handling.
- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated Ansible playbooks. This can be addressed by maintaining the same configuration outputs.
- **Test Kitchen**: Deciding whether to migrate from Test Kitchen to Ansible Molecule or maintain Test Kitchen for testing Ansible playbooks.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **chef-automate-deploy.sh** (moderate complexity): Convert to Ansible playbook with proper idempotence and error handling
4. **chef-server-deploy.sh** (moderate complexity): Convert to Ansible playbook with proper idempotence and error handling

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployments (based on the README.md content).
2. The InSpec tests are intended to be maintained as part of the compliance validation strategy.
3. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure values in production.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The Apache configuration in the Ansible playbooks is intended to be a basic example and may need enhancement for production use.
6. The Chef Automate and Chef Infra Server deployment is still relevant to the organization's needs and should be migrated rather than deprecated.