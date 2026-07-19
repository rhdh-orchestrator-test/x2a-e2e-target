# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating security compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 2-3 weeks for a complete migration, with the majority of time spent on testing and validation.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS support, creates self-signed certificates, and deploys a simple website. Migration considerations: Already in Ansible format, but should be reviewed for best practices and potential improvements.

- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2. Migration considerations: Already in Ansible format, but should be reviewed for current security best practices.

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations: Replace with Ansible-native testing frameworks like Molecule.

- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS website configuration. Migration considerations: Convert to Ansible-compatible testing framework like Molecule with Testinfra or Ansible's assert module.

- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for validating SSH security configuration. Migration considerations: Convert to Ansible-compatible testing framework.

- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration considerations: Replace with Ansible playbook for infrastructure deployment.

- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration considerations: Replace with Ansible playbook for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for simple tests
  - Option 2: Use Molecule with Testinfra for more complex testing
  - Option 3: Use Ansible Lint for static code analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for CI/CD pipelines
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The current playbooks enforce TLSv1.2 and disable SSLv3 to address the POODLE vulnerability. Migration should maintain or enhance these security settings, potentially upgrading to TLSv1.3.

- **Self-signed Certificates**: The current solution uses self-signed certificates. Consider integrating with Let's Encrypt for production environments.

- **SSH Hardening**: The InSpec tests validate SSH security configurations. Ensure these security checks are maintained in the Ansible migration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL/TLS certificate references in Apache configuration
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions and may require additional tooling.
  - Mitigation: Create a mapping document for InSpec to Ansible test assertions and validate each test case individually.

- **Infrastructure Deployment**: Replacing the Chef Automate and Chef Infra Server deployment scripts with Ansible will require understanding of the Chef infrastructure components.
  - Mitigation: Create Ansible roles for each component of the infrastructure and test thoroughly in a staging environment.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Review and optimize existing playbooks
   - Implement Ansible best practices (roles, variables, etc.)

2. **Testing Framework** (Moderate complexity)
   - Convert InSpec tests to Ansible-compatible testing framework
   - Implement CI/CD pipeline for automated testing

3. **Infrastructure Deployment** (High complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Infra Server deployment scripts
   - Implement Ansible Vault for secrets management

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
2. The migration will maintain the same functionality as the current implementation.
3. The InSpec tests represent the compliance requirements that must be maintained in the migrated solution.
4. The Chef Automate and Chef Infra Server deployment scripts are used for setting up the infrastructure and are not part of the application deployment.
5. The hardcoded credentials in the scripts are for demonstration purposes and will be replaced with secure alternatives in the production environment.
6. The self-signed certificates are acceptable for the target environment, or will be replaced with trusted certificates.