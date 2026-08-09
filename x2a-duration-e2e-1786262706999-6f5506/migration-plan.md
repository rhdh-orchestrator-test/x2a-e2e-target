# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be a demonstration or example repository rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec profiles for compliance testing
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The main focus will be on preserving the compliance testing functionality while consolidating all configuration management into Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that checks SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible for both provisioning and verification.
- `index.html`: Simple HTML file used for testing the web server. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic compliance checks
  - Option 2: Use Ansible Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Or update Test Kitchen configuration to use Ansible for both provisioning and verification

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure deployment
  - Consider migrating to Ansible Tower/AWX for enterprise features

### Security Considerations

- **SSL Configuration**: The current playbooks configure SSL for Apache. Migration should:
  - Preserve the SSL hardening (disabling SSLv3, enabling only TLSv1.2)
  - Use Ansible's `openssl_*` modules consistently
  - Consider using Let's Encrypt integration instead of self-signed certificates

- **SSH Hardening**: The InSpec profile checks SSH security. Migration should:
  - Create equivalent Ansible tasks to enforce SSH security settings
  - Implement idempotent checks for SSH configuration

- **Credentials Management**: The deployment scripts contain hardcoded credentials:
  - Replace with Ansible Vault for secure credential storage
  - Use variables for all sensitive information
  - Document: 3 credential sets identified in deployment scripts (username, password, email)

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks:
  - Challenge: InSpec has rich testing capabilities specifically designed for compliance
  - Mitigation: Consider keeping InSpec as a testing tool but invoking it from Ansible, or use Ansible's assert module with detailed conditions

- **Test Kitchen Integration**: Ensuring the testing workflow remains smooth:
  - Challenge: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Either migrate to Molecule or update the Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and optimize according to best practices
   - Consolidate into roles if appropriate
   - Add documentation

2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium risk
   - Convert to Ansible playbooks
   - Implement secure credential management
   - Test thoroughly

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): High complexity
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native testing)
   - Implement and validate equivalent tests
   - Update documentation

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production use
2. The target environment will continue to be Ubuntu 20.04 or similar
3. Vagrant will continue to be used for local testing
4. The compliance requirements represented in the InSpec tests must be preserved
5. The deployment scripts are examples and may not need to be fully migrated if Chef Automate/Server is not part of the target infrastructure
6. No external dependencies or integrations beyond what's visible in the repository
7. No specific performance requirements for the migrated solution