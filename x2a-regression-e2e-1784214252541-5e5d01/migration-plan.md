# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Bash scripts for Chef Automate/Chef Infra Server deployment. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests that need to be migrated to Ansible-compatible testing frameworks
2. Bash scripts for Chef infrastructure deployment that need to be converted to Ansible playbooks

The complexity is moderate, with the primary challenge being the migration of InSpec tests to an Ansible-compatible testing framework. The estimated timeline for migration is 1-2 weeks, depending on team familiarity with Ansible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible/
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS configuration testing, SSL/TLS protocol verification, website availability testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Automated deployment of Chef infrastructure, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible and InSpec integration. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. This is already in Ansible format and can be kept with minor adjustments.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. This is already in Ansible format and can be kept with minor adjustments.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include converting to an Ansible playbook with appropriate variables.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include converting to an Ansible playbook with appropriate variables.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Determine if these components are still needed or if they can be replaced with Ansible Tower/AWX or other configuration management solutions

### Security Considerations

- **SSL/TLS Configuration**: The current implementation focuses on securing Apache with TLS 1.2 and disabling older protocols. Migration should maintain or enhance this security posture.
  - Approach: Use Ansible's `openssl_*` modules as already demonstrated in the existing playbooks

- **SSH Hardening**: The InSpec profile checks for secure SSH configuration (disabling root login).
  - Approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible assertions or Molecule tests requires careful mapping of test logic.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Chef Server Deployment**: If Chef Server is still required in the environment, determining how to manage it with Ansible.
  - Mitigation: Create an Ansible role for Chef Server management or consider migrating completely away from Chef

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. Update to follow best practices and integrate with Ansible Vault for any secrets.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity. Convert to Ansible assertions or Molecule tests while maintaining the same compliance checks.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity. Determine if Chef infrastructure is still needed or if it can be replaced entirely with Ansible. If needed, convert to Ansible playbooks.

### Assumptions

1. The Chef InSpec tests are used primarily for compliance verification and not for broader infrastructure testing.

2. The deployment scripts for Chef Automate and Chef Infra Server are used for setting up a testing or development environment, not production infrastructure.

3. The target environment will continue to be Ubuntu-based systems, as the current configurations are Ubuntu-specific.

4. The team has the necessary expertise in Ansible or will receive training as part of the migration process.

5. There is no direct integration with CI/CD pipelines evident in the repository, but this might be a consideration for the migration.

6. The hardcoded credentials in the deployment scripts are for testing purposes only and will be properly secured in the migrated solution.

7. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and can be used as reference for the migration style and approach.