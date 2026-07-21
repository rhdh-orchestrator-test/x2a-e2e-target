# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Ansible playbooks, Chef InSpec tests, and Chef Automate/Chef Server deployment scripts. The migration scope is relatively small, focusing on standardizing the entire repository to use Ansible exclusively. The primary components requiring migration are:

1. Two shell scripts for deploying Chef Automate and Chef Server
2. InSpec test files that need to be converted to Ansible-compatible testing frameworks

The existing Ansible playbooks can be retained with minimal modifications. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and straightforward conversion paths.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

- **website_https_verification**:
    - Description: InSpec test profile for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol checks

- **ssh_security_profile**:
    - Description: InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be migrated to use Ansible's native testing framework or Molecule.
- `README.md`: Repository documentation that will need updating to reflect the migration to Ansible-only.
- `chef-and-ansible/README.md`: Documentation for the Chef InSpec with Ansible examples, will need updating to reflect the new Ansible-only approach.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml and supported by the Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Lint for static analysis
  - Option 2: Molecule for comprehensive testing
  - Option 3: ansible-test for integration testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source upstream of Ansible Tower)
  - Ansible Automation Platform (commercial)

### Security Considerations

- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault:
  - Username: jtonello
  - Password: password
  - Email: jtonello@chef.lab

- **SSL Configuration**: The existing playbooks properly configure TLSv1.2 and disable insecure protocols. This security hardening should be preserved in the migrated solution.

- **SSH Hardening**: The SSH security profile tests for root login restrictions. This security check should be implemented as an Ansible task and included in the migrated solution.

- **Vault/secrets management**:
  - 2 hardcoded credentials in the Chef deployment scripts (username/password)
  - Self-signed SSL certificates generated in the website_https.yml playbook

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec has a domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use Ansible Lint custom rules and Molecule verifiers to implement equivalent tests

- **Chef Automate Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate functionality:
  - Challenge: Chef Automate provides compliance reporting, infrastructure visibility, and application automation
  - Mitigation: Implement AWX/Ansible Tower with appropriate dashboards and reporting plugins

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and update to current Ansible best practices
   - Add documentation and comments

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert to Molecule tests or Ansible assert tasks
   - Ensure equivalent coverage for security checks

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible playbooks to replace Chef Automate/Server deployment
   - Implement Ansible Vault for credential storage
   - Document migration path for existing Chef users

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. Vagrant will continue to be used for development/testing environments
3. The security compliance requirements will remain the same after migration
4. No external Chef cookbooks or resources are being used beyond what's in the repository
5. The Chef Automate/Server deployment is for demonstration purposes and not a production environment
6. The InSpec tests are primarily used for local testing and not integrated into a larger compliance framework
7. No custom Chef resources or handlers are being used that would require special migration handling