# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already, with Chef InSpec tests and Chef server deployment scripts being the main migration targets.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: A set of Ansible playbooks and Chef InSpec tests for deploying and validating a secure HTTPS website
    - Path: chef-and-ansible
    - Technology: Ansible playbooks with Chef InSpec tests
    - Key Features: HTTPS configuration, SSL certificate generation, Apache configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the migration.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment. Can be preserved as-is.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Will need to be converted to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need to be converted to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Will need to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Will need to be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing frameworks:
  - **Option 1**: Ansible Molecule for testing Ansible roles and playbooks
  - **Option 2**: Ansible Lint for static analysis of playbooks
  - **Option 3**: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - **Option 1**: Ansible Molecule for testing infrastructure
  - **Option 2**: Simple Vagrant/Docker scripts invoked directly by CI/CD pipeline

- **Chef Automate/Infra Server**: Replace with:
  - **Option 1**: Ansible AWX/Tower for centralized management
  - **Option 2**: GitLab CI/CD or Jenkins for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated solution.
  - Migration approach: Preserve the existing Ansible tasks that configure SSL/TLS settings.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. This security check should be maintained.
  - Migration approach: Convert the InSpec test to an equivalent Ansible assert or check task.

- **Self-signed Certificates**: The playbooks generate self-signed certificates for HTTPS.
  - Migration approach: Preserve the existing Ansible OpenSSL tasks, but consider adding support for Let's Encrypt as an alternative.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The Chef server deployment scripts contain hardcoded usernames and passwords.
  - Migration approach: Use Ansible Vault to secure these credentials in the migrated playbooks.
  - Count: 2 credential sets (username/password) in the deployment scripts.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Ansible's assert module for simple tests, or consider maintaining InSpec as a separate tool invoked by Ansible for complex compliance testing.

- **Test Kitchen Replacement**: Finding an equivalent to Test Kitchen for testing Ansible playbooks.
  - Mitigation: Adopt Ansible Molecule as a replacement for Test Kitchen, as it provides similar functionality for Ansible playbooks.

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible playbooks.
  - Mitigation: Create Ansible roles for deploying alternative infrastructure management solutions like AWX/Tower or GitLab CI/CD.

### Migration Order

1. **InSpec Tests** (Medium complexity): Convert InSpec tests to Ansible-compatible testing frameworks.
   - `chef-and-ansible/tests/website_https_verify.rb`
   - `chef-and-ansible/tests/ssh_profile.rb`

2. **Test Kitchen Configuration** (Low complexity): Replace Test Kitchen with Ansible Molecule or similar.
   - `chef-and-ansible/kitchen.yml`

3. **Chef Server Deployment Scripts** (High complexity): Convert to Ansible playbooks.
   - `setup-automate/deploy-automate.sh`
   - `setup-automate/deploy-chef-server.sh`

### Assumptions

1. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are working correctly and do not need significant modifications.
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
3. The organization is moving away from Chef entirely, including Chef Automate and Chef Infra Server.
4. The InSpec tests are currently being used for compliance validation and this functionality needs to be preserved.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives in the production environment.
6. The self-signed certificates are acceptable for the use case, but production environments might require proper CA-signed certificates.
7. The migration will maintain the same level of security and compliance checking as the original implementation.