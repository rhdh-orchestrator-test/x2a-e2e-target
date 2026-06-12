# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a test page. Can be directly used in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (based on setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in assert module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a complementary testing tool if its compliance capabilities are valued

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: The SSH root login compliance check must be preserved in the new testing framework
- **Self-signed Certificates**: The certificate generation process should be maintained or improved in the migrated solution
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in setup-automate scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules. The compliance metadata (STIG IDs, CCI references) in the InSpec controls should be preserved in comments or structured variables.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules and develop a consistent pattern for preserving compliance metadata.

- **Test Kitchen to Molecule**: The testing workflow will need to be adapted from Test Kitchen to Molecule.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen configuration.

- **Chef Automate Deployment**: The Chef Automate and Chef Server deployment scripts will need to be completely reimagined as they are specifically for deploying Chef infrastructure.
  - Mitigation: Determine if an equivalent Ansible infrastructure is needed (e.g., AWX/Tower) or if this component can be eliminated from the migration scope.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires complete reimagining)

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, eliminating the need for Chef InSpec.
2. The compliance testing capabilities provided by InSpec are still required in the migrated solution.
3. The Chef Automate and Chef Server deployment scripts may be out of scope for the migration if there's no equivalent Ansible infrastructure required.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The self-signed certificate approach is acceptable for the migrated solution rather than integrating with a certificate authority.
6. The current Test Kitchen testing workflow needs to be preserved in some form in the migrated solution.
7. The hardcoded credentials in the setup scripts need to be secured in the migrated solution.