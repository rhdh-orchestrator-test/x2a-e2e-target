# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a test page. Can be directly used in Ansible without modification.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to ansible-test framework

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security hardening measures are preserved in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL protocol restrictions (TLSv1.2) in the migrated playbooks.

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Ensure these checks are implemented in the Ansible playbooks.
  - Migration approach: Create Ansible tasks that enforce the same SSH security configurations and add post-tasks to verify compliance.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing mechanisms will require careful mapping of test assertions.
  - Mitigation strategy: Create a mapping document for InSpec resources to Ansible modules/assertions and validate each test conversion individually.

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible roles.
  - Mitigation strategy: Create an Ansible role that performs the same system configurations and uses the Chef API for user/organization management.

### Migration Order

1. **website_https.yml** (low risk, already Ansible) - Minimal changes needed, just formatting and best practices
2. **poodle_fix.yml** (low risk, already Ansible) - Minimal changes needed, just formatting and best practices
3. **InSpec Tests** (moderate complexity) - Convert to Ansible-native testing
4. **Chef Deployment Scripts** (high complexity) - Convert to Ansible roles for infrastructure deployment

### Assumptions

1. The primary goal is to migrate all components to pure Ansible without any Chef dependencies.
2. The InSpec tests need to be converted to Ansible-native testing mechanisms rather than keeping InSpec.
3. The deployment scripts for Chef Automate and Chef Infra Server are to be converted to Ansible playbooks that would deploy alternative solutions, as keeping Chef components would contradict the migration goal.
4. The target environment will remain Ubuntu 20.04 on Vagrant VMs.
5. There are no external data sources or integrations beyond what's visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.