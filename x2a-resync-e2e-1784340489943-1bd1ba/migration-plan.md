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
    - Key Features: SSL/TLS configuration, Apache web server setup, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for setting up an HTTPS website. Migration consideration: Keep as-is, but update to follow current Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Keep as-is, but update to follow current Ansible best practices.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for verifying HTTPS website. Migration consideration: Convert to Ansible-compatible testing framework like Molecule with Testinfra or Goss.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test for SSH security compliance. Migration consideration: Convert to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook or remove if not needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs (mentioned in setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Ansible Molecule with Testinfra for Python-based testing
  - Option 2: Ansible Molecule with Goss for YAML-based testing
  - Option 3: Use the ansible.builtin.assert module for simple tests

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for CI/CD pipelines
  - Compliance scanning can be handled by OpenSCAP with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3. Migration approach: Maintain these security settings but update to include TLS 1.3 if appropriate.

- **SSH Security**: InSpec tests verify SSH root login is disabled. Migration approach: Convert to Ansible-compatible tests while maintaining the same security checks.

- **Self-signed Certificates**: The playbooks generate self-signed certificates. Migration approach: Maintain this functionality but consider adding Let's Encrypt integration as an option.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password). Migration approach: Replace with Ansible Vault for secure credential storage.
  - SSL/TLS certificate references in website_https.yml. Migration approach: Maintain the same file paths but use Ansible Vault for any sensitive data.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing approaches. Mitigation: Start with simple tests and gradually convert more complex ones.

- **Chef Server Deployment**: The Chef server deployment scripts need to be completely rewritten as Ansible playbooks. Mitigation: Break down the scripts into smaller tasks and convert each one individually.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible): Update existing playbooks to follow current Ansible best practices.
2. **InSpec Tests** (Medium complexity): Convert InSpec tests to Ansible-compatible testing frameworks.
3. **Chef Server Deployment Scripts** (High complexity): Convert bash scripts to Ansible playbooks.

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality.
2. The existing Ansible playbooks are working correctly and don't need significant changes beyond best practices updates.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The self-signed certificate approach is acceptable for the migrated solution.
5. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure alternatives.
6. The Chef Automate and Chef Infra Server deployment scripts are still needed in some form rather than being eliminated entirely.