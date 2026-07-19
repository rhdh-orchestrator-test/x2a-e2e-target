# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations with a focus on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website and SSH configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL protocol security, SSH security configuration

- **chef-automate-setup**:
    - Description: Shell scripts to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Installs Chef Automate and Chef Infra Server, creates users and organizations

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for remediating SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test for basic verification
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to Ansible assert tasks
  - Option 4: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible-specific CI/CD pipelines

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for simpler CI/CD pipelines

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert directly to Ansible tasks with identical functionality
  - Ensure TLSv1.2 requirement is maintained

- **SSH Security**: The SSH compliance tests must be preserved
  - Approach: Convert InSpec tests to Ansible assert tasks or maintain as separate InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible equivalents
  - Mitigation: Use Ansible's assert module for basic tests, consider maintaining InSpec for complex compliance testing

- **Compliance Reporting**: Maintaining compliance reporting capabilities
  - Mitigation: Integrate with compliance tools like OpenSCAP or maintain InSpec for reporting

- **User/Organization Management**: Replacing Chef user and organization management
  - Mitigation: Create Ansible roles for user management that match Chef's functionality

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add documentation and improve variable usage

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Consider merging with website-https as an optional security enhancement

3. **InSpec tests** (moderate complexity)
   - Decide on testing strategy (convert to Ansible or maintain InSpec)
   - Implement chosen approach while preserving test coverage

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to replace Chef Automate/Infra Server deployment
   - Implement user and organization management in Ansible

### Assumptions

1. The primary goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment
2. Compliance testing is a critical requirement that must be preserved in the migration
3. The current setup is used for demonstration/educational purposes rather than production
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for local development/testing
6. The security requirements (TLS 1.2, SSH hardening) must be maintained
7. User credentials in the deployment scripts are examples and will be replaced with secure values