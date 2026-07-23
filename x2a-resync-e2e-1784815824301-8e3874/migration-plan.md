# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a pure Ansible solution. The repository primarily consists of:

1. Example Ansible playbooks with Chef InSpec tests for compliance automation
2. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and Chef-related deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which need minimal changes) and medium complexity for the Chef server deployment scripts (which need to be reimplemented as Ansible roles).

## Module Migration Plan

This repository contains both Ansible playbooks and Chef deployment scripts that need individual migration planning:

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
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Consider maintaining InSpec as a standalone testing tool that can work with Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific Test Kitchen plugin if maintaining Test Kitchen is preferred

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for enterprise automation platform
  - Option 2: GitLab CI/CD with Ansible for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the Ansible migration maintains:
  - Proper TLS protocol settings (TLS 1.2 enabled, older protocols disabled)
  - Self-signed certificate generation
  - Proper file permissions for certificates

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Ensure:
  - SSH hardening is implemented in the Ansible roles
  - Compliance checks are maintained in the new testing framework

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in each deployment script

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing requires:
  - Understanding the compliance requirements being tested
  - Implementing equivalent checks using Ansible's assertion capabilities
  - Maintaining the same level of compliance validation

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible requires:
  - Creating Ansible roles for Chef server installation (if still needed)
  - Implementing idempotent configuration that matches the shell script functionality
  - Handling user and organization creation through Ansible

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk, minimal changes needed
   - Update to follow current Ansible best practices
   - Integrate with new testing framework

2. **Testing Framework**:
   - Medium complexity
   - Convert InSpec tests to Ansible-native testing or Molecule
   - Ensure compliance checks are maintained

3. **Chef Deployment Scripts**:
   - Higher complexity
   - Create Ansible roles to replace shell scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration purposes, as indicated by the README.md mentioning "working examples" and "how-tos".
2. The Chef deployment scripts are used for setting up Chef infrastructure, which may be replaced entirely by Ansible AWX/Tower.
3. The InSpec tests are valuable for compliance and should be maintained in some form.
4. The Ansible playbooks are already well-structured and need minimal changes.
5. There are no external dependencies or integrations not visible in the repository.
6. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management.