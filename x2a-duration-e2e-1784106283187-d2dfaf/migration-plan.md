# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components:

1. A Chef InSpec and Ansible integration example in the `chef-and-ansible` directory
2. Chef Automate and Chef Infra Server deployment scripts in the `setup-automate` directory

The migration complexity is **LOW** as most of the content is already in Ansible format, with the primary focus being on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef server deployment scripts with Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in SSL/TLS configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enforces TLSv1.2 in Apache configuration

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration
- `index.html`: Sample HTML file for website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts are designed to work on cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for testing
  - Option 2: Keep InSpec tests but integrate with Ansible using ansible_inspec_callback plugin
  - Option 3: Convert to ansible-lint custom rules for compliance checks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and UI
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance automation can be handled by OpenSCAP or Ansible's built-in security automation

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS hardening (POODLE fix)
  - Migration approach: Preserve the same security configurations in Ansible tasks
  - Ensure the same TLS protocol restrictions are maintained

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create equivalent Ansible tasks to enforce SSH security settings
  - Add Ansible assertions or molecule tests to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Molecule with testinfra or maintain InSpec as a separate tool called from Ansible

- **Chef Server Replacement**: Replacing Chef Server functionality with Ansible equivalents
  - Mitigation: Implement AWX/Tower for web UI and role-based access control
  - Use Git repositories for configuration management instead of Chef Server's centralized approach

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible format)
   - Only needs minor adjustments to follow Ansible best practices
   - Update testing framework

2. **poodle-vulnerability-fix** (low risk, already in Ansible format)
   - Only needs minor adjustments to follow Ansible best practices
   - Update testing framework

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-compatible testing frameworks
   - Ensure all compliance checks are preserved

4. **Chef Server Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Replace Chef-specific functionality with Ansible equivalents

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are essential and their functionality must be preserved in the migration
3. The deployment scripts are used for setting up test environments and not production systems
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. No complex data bags, environments, or Chef roles are in use that would require migration
8. The Apache configuration specifics (virtual hosts, SSL settings) must be preserved exactly