# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible
    - Technology: Chef InSpec (for testing) and Ansible (for configuration)
    - Key Features: HTTPS configuration, SSL/TLS security settings, web server deployment

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: User creation, organization setup, Chef server configuration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server with HTTPS. Can be preserved as-is in the migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be preserved as-is in the migration.
- `chef-and-ansible/index.html`: Sample HTML file used in the web server deployment. Can be preserved as-is.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the setup scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider ansible-test for unit testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for CI/CD pipelines
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure SSL/TLS settings for web servers. Ensure these security settings are preserved in the migration.
  - Migration approach: Preserve the existing Ansible tasks that configure SSL/TLS settings.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this security check is preserved.
  - Migration approach: Convert the InSpec SSH test to Ansible assert tasks or Molecule verify steps.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The deploy-automate.sh and deploy-chef-server.sh scripts contain hardcoded usernames and passwords. These should be moved to Ansible Vault.
  - Count: 2 credential sets detected (username/password in each deployment script)

### Technical Challenges

- **Test Conversion**: Converting Chef InSpec tests to Ansible-native testing solutions.
  - Mitigation: Use Ansible's assert module for simple tests, and Molecule for more complex testing scenarios.

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment, or preferably replace with AWX/Tower deployment.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **InSpec Tests** (Medium complexity)
   - Convert website_https_verify.rb to Ansible Molecule tests
   - Convert ssh_profile.rb to Ansible Molecule tests

3. **Chef Server Deployment Scripts** (Higher complexity)
   - Convert deploy-chef-server.sh to Ansible playbook
   - Convert deploy-automate.sh to Ansible playbook or replace with AWX/Tower deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, rather than being a production deployment system.

2. The Chef InSpec tests are used for validation only and do not contain any remediation logic that would need to be migrated.

3. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production environments.

5. The organization is planning to fully migrate away from Chef tools (including InSpec) to an Ansible-only solution.

6. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and do not need functional changes.