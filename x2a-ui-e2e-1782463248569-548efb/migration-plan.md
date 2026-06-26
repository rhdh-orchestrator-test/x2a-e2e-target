# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of Ansible playbooks with Chef InSpec tests and Chef Automate/Chef Server deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for validating HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH root login compliance check

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts with Chef commands
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file used for testing the web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Migrate InSpec tests to Ansible's built-in `assert` module or consider using:
    - ansible-lint for static analysis
    - Molecule for testing
    - ansible.builtin.command with grep/awk for validation checks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - molecule-vagrant plugin if Vagrant integration is needed

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable older protocols
  - Migration approach: Maintain the same security settings in migrated Ansible playbooks
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Ensure SSH hardening is included in the migrated Ansible playbooks
  - Add explicit SSH configuration tasks to enforce security settings

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible verification methods
  - Mitigation: Use Ansible's assert module with command/shell modules to perform similar checks
  - Consider implementing custom Ansible modules if complex validation is required

- **Chef Automate/Server Deployment**: Replacing Chef server deployment scripts
  - Mitigation: Create Ansible roles for infrastructure management that were previously handled by Chef
  - Consider if Chef Automate/Server is still needed or if it can be replaced with Ansible Tower/AWX

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better organization

2. **poodle_fix.yml** (already in Ansible format, low risk)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https role as a security enhancement

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef Deployment Scripts** (high complexity)
   - Determine if Chef Automate/Server is still needed
   - If needed, create Ansible playbooks to deploy Chef infrastructure
   - If not needed, document the deprecation

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The Chef Automate and Chef Server deployment scripts may not be needed if moving to a pure Ansible solution
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. The SSL/TLS security requirements will remain the same or become more stringent
7. No external dependencies or integrations beyond what's visible in the repository