# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
2. Consolidating the existing Ansible playbooks and InSpec tests into a standardized Ansible structure
3. Replacing Chef InSpec tests with equivalent Ansible testing mechanisms (e.g., ansible-test, molecule)

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase size.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
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
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance checks

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test for integration testing
  - Option 2: Use Molecule for playbook testing
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Or continue using Test Kitchen with the ansible provisioner

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure provisioning
  - Consider using ansible-galaxy for role organization

### Security Considerations

- **SSL/TLS Configuration**: The existing playbooks configure Apache with TLS 1.2 and disable vulnerable protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Create an Ansible role for Apache hardening that implements the same TLS configurations

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role that applies SSH hardening and includes idempotent checks

- **Self-signed Certificates**: The playbook generates self-signed certificates.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) but consider adding support for Let's Encrypt as an improvement

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods.
  - Mitigation: Use ansible.builtin.assert or ansible.builtin.command with grep/awk to verify configurations

- **Chef Automate Deployment**: Ensuring the Chef Automate deployment process is correctly translated to Ansible.
  - Mitigation: Create a dedicated role for Chef Automate deployment that follows the same steps as the bash script

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format, just need restructuring
2. **InSpec Tests** (chef-and-ansible/tests/*.rb): Medium complexity to convert to Ansible testing mechanisms
3. **Chef Deployment Scripts** (setup-automate/*.sh): Higher complexity to convert to idempotent Ansible playbooks

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content.
2. The Chef Automate deployment scripts are intended for on-premises or cloud VM deployment, not container-based deployments.
3. The hardcoded credentials in the deployment scripts are example values and not actual production credentials.
4. The InSpec tests are meant to be run as part of Test Kitchen validation rather than as standalone compliance checks.
5. The existing Ansible playbooks are already functional and just need reorganization rather than functional changes.