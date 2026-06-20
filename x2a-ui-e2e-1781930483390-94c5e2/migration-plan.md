# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests for compliance verification
2. Chef Automate/Chef Server deployment scripts

The migration complexity is **LOW to MEDIUM** as most of the repository already contains Ansible playbooks. The primary focus will be on replacing Chef InSpec tests with Ansible-compatible testing frameworks and migrating Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website configuration and SSH security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSL/TLS protocol verification, SSH configuration compliance checks, web server functionality testing

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts with Chef server commands
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-compatible testing framework configuration.
- `website_https.yml`: Ansible playbook for configuring HTTPS website. Already in Ansible format, no migration needed.
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Already in Ansible format, no migration needed.
- `index.html`: Sample HTML file used by the website playbook. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: Ansible's assert module for basic compliance checks
  - Option 3: Integration with other compliance tools like OSCAP or Lynis

- **Chef Automate/Chef Server**: Replace deployment scripts with Ansible roles for:
  - Configuration management platform deployment
  - User and organization management
  - Consider migrating to Ansible AWX/Tower as a replacement for Chef Automate

### Security Considerations

- **SSL/TLS Configuration**: The current InSpec tests verify proper TLS configuration (disabling SSLv3, enabling TLSv1.2). Migration must ensure these security checks remain in place.
  - Approach: Create Ansible tasks using the assert module to verify SSL configurations

- **SSH Security Compliance**: The SSH profile checks for secure SSH configuration (disabling root login).
  - Approach: Create Ansible tasks to enforce and verify SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated dynamically in the playbooks, which is a good practice to maintain

### Technical Challenges

- **Test Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions.
  - Mitigation: Create a test mapping document to ensure all compliance checks are preserved

- **Deployment Script Conversion**: The Chef server deployment scripts contain specific Chef commands that need Ansible equivalents.
  - Mitigation: Research Ansible roles for deploying alternative configuration management platforms or create custom roles

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - No changes needed for website_https.yml and poodle_fix.yml

2. **InSpec Tests** (Medium complexity)
   - Convert website_https_verify.rb to Ansible Molecule tests or assert tasks
   - Convert ssh_profile.rb to Ansible security checks

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible roles to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The hardcoded credentials in the deployment scripts are examples and not used in production.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The team is willing to adopt alternative compliance testing frameworks to replace Chef InSpec.
5. There are no additional Chef cookbooks or resources not visible in the provided repository structure.
6. The migration will focus on maintaining the same functionality rather than enhancing it.
7. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification.