# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used as examples for demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes setup scripts for Chef Automate and Chef Infra Server. The migration scope is relatively small, as most of the Ansible components are already in place and only the Chef InSpec tests and setup scripts need to be migrated to pure Ansible solutions.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Technologies**: Chef InSpec, Ansible Playbooks, Bash Scripts

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef server setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance tagging (STIG, CCI)

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/index.html`: Simple HTML file used in the website example. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Ansible Lint for static analysis
  - **Option 2**: Molecule for integration testing
  - **Option 3**: Ansible's assert module for runtime validation

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - **Option 1**: Ansible Tower/AWX for orchestration and reporting
  - **Option 2**: GitLab CI/CD or Jenkins for pipeline automation
  - **Option 3**: Prometheus and Grafana for monitoring and reporting

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) with proper secret management.

- **SSH Security**: The InSpec tests check for SSH root login configuration.
  - Migration approach: Create equivalent Ansible playbook with assert module to verify SSH configuration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault.
  - Self-signed certificates should be managed securely.
  - Count of credentials detected: 3 (username, password, SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests.
  - Mitigation: Create custom Ansible modules or use the assert module with appropriate conditionals.

- **Chef Server Setup**: Replacing Chef server deployment with Ansible management infrastructure.
  - Mitigation: Document alternative approaches using Ansible Tower/AWX or other CI/CD tools.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor adjustments for best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires converting Ruby-based tests to Ansible assertions or Molecule tests.

3. **Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires replacing Chef server infrastructure with Ansible-native solutions.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment.
2. The InSpec tests are used for compliance validation rather than as part of a larger compliance framework.
3. There is no existing Ansible Tower/AWX infrastructure to replace Chef Automate functionality.
4. The team has expertise in both Chef and Ansible technologies.
5. There are no external dependencies or integrations not visible in the repository.
6. The migration is focused on technical implementation rather than organizational process changes.
7. The hardcoded credentials in the setup scripts are for demonstration purposes only.