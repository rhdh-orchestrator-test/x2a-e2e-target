# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance checks are preserved in the new implementation

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration security check, STIG compliance verification

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. Can be directly used in Ansible without modification.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic but with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP or DISA STIG Ansible roles

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Set system parameters (hostname, sysctl values)
  - Install and configure alternative compliance platforms (options include:)
    - AWX/Ansible Tower
    - Prometheus with compliance exporters
    - OpenSCAP with SCAP Workbench

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Migration approach: Create an Ansible role for Apache security hardening that includes the SSL/TLS configurations

- **SSH Security**: The SSH root login compliance check must be preserved
  - Migration approach: Create an Ansible role that implements the same SSH security controls and includes verification tasks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing**: Converting Chef InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation strategy: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Deployment Scripts**: The Chef Automate/Infra Server deployment scripts contain specific configurations that need to be mapped to alternative solutions
  - Mitigation strategy: Identify functional equivalents in the Ansible ecosystem for each Chef component

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - No migration needed, already in Ansible format
   - May need refactoring into roles for better organization

2. **poodle_fix.yml** (low risk, already Ansible)
   - No migration needed, already in Ansible format
   - Consider merging with website_https.yml as a security role

3. **Chef InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible playbooks
   - Replace Chef-specific components with Ansible alternatives

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies
2. Compliance testing is a critical requirement that must be preserved
3. The deployment scripts are used for setting up test/demo environments, not production systems
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The hardcoded credentials in the deployment scripts are not used in production environments
7. The self-signed certificates are for testing purposes only