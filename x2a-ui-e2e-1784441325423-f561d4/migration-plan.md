# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating security compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** as most of the content is already in Ansible format, with the primary focus being on converting Chef InSpec tests to Ansible-compatible testing frameworks and replacing Chef server deployment scripts with Ansible playbooks.

**Estimated Timeline**: 2-3 weeks for a complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks and Chef InSpec tests for HTTPS configuration and compliance testing
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks and Chef InSpec)
    - Key Features: Apache HTTPS configuration, SSL security testing, Test Kitchen integration

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS using self-signed certificates
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `chef-and-ansible/README.md`: Documentation for Chef InSpec with Ansible integration
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test for validating SSH security
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Migrate to Ansible Molecule for testing
  - **Option 2**: Use ansible-test framework
  - **Option 3**: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The current playbooks properly configure TLSv1.2 and disable vulnerable protocols. This should be maintained in the migrated solution.
  - Migration approach: Preserve the same SSL configuration in the Ansible playbooks

- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint to verify SSH security

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys
  - Document the count and type of credentials detected per module:
    - setup-automate: 1 password in plaintext

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Map InSpec resources to equivalent Ansible modules or assertions
  - Example: InSpec's `describe port(443)` can be replaced with Ansible's `wait_for` module with `port: 443`

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible playbooks
  - Mitigation: Create Ansible roles for infrastructure management that were previously handled by Chef server
  - Consider using AWX/Ansible Tower as a replacement for Chef Automate's UI and workflow capabilities

### Migration Order

1. **chef-and-ansible/website_https.yml** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add documentation and improve variable naming

2. **chef-and-ansible/poodle_fix.yml** (low risk, already in Ansible)
   - Integrate with the main website HTTPS playbook
   - Add conditional logic for different Apache versions

3. **chef-and-ansible/tests** (medium complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure all security checks are preserved

4. **setup-automate** (high complexity)
   - Create Ansible playbooks to replace Chef server deployment
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible integration, not for production deployment
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. The security requirements include proper HTTPS configuration and SSH hardening
4. No external dependencies or complex infrastructure is required beyond what's explicitly defined in the playbooks
5. The Chef server deployment scripts are used for setting up test environments, not production infrastructure
6. No custom Chef cookbooks or complex Chef-specific functionality needs to be migrated
7. The migration will maintain the same level of security validation currently provided by InSpec tests