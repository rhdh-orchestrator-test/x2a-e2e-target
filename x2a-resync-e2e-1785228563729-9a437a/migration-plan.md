# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, with only a few Ansible playbooks that need to be updated to current Ansible best practices, and Chef InSpec tests that need to be converted to Ansible-compatible testing frameworks. The shell scripts for Chef infrastructure deployment will need to be replaced with Ansible playbooks for infrastructure provisioning.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Risk Level**: Low

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

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

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use ansible-test for validation
  - Option 3: Use Molecule with testinfra for infrastructure testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with specific security settings:
  - Migration should maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Self-signed certificate generation should be preserved or improved

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled:
  - Migration should include equivalent Ansible tasks to enforce this security control
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts need to be moved to Ansible Vault
  - Password 'password' in the deployment scripts should be replaced with secure vault-stored credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks will require mapping InSpec resources to Ansible modules or testinfra methods
  - Mitigation: Create a mapping document for common InSpec resources to their Ansible equivalents

- **Chef Automate Deployment**: Replacing the Chef Automate deployment scripts with Ansible playbooks
  - Mitigation: Research Ansible roles for Chef server deployment or create custom roles based on the official Chef documentation

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need updates to current best practices
2. **Testing Framework**: Convert InSpec tests to Ansible-compatible testing framework
3. **Chef Deployment Scripts**: Replace with Ansible playbooks for infrastructure provisioning

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README indicating these are examples for blog posts
2. The InSpec tests are used for validation of infrastructure rather than continuous compliance monitoring
3. The deployment scripts are templates that would be customized for actual deployments
4. No external dependencies or inventory files are present beyond what's visible in the repository
5. The target environment for the migrated Ansible playbooks will continue to be Ubuntu 20.04 or newer
6. No complex data structures or external variable sources are being used
7. No integration with external systems beyond basic web server functionality
8. No specific CI/CD pipeline integration is required