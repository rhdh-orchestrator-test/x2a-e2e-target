# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible compliance checks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file used for testing the web server deployment. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native compliance solutions:
  - Option 1: Convert InSpec tests to Ansible assert tasks
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with OpenSCAP or other compliance tools

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible tasks
  
- **SSH Hardening**: The SSH compliance checks need to be converted to Ansible
  - Approach: Convert InSpec SSH checks to Ansible tasks that verify the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec tests to Ansible assertions requires careful mapping of test logic
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  
- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI references) that needs preservation
  - Mitigation: Store compliance metadata in Ansible task documentation or in separate YAML files

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible requires understanding of Chef infrastructure
  - Mitigation: Create Ansible roles that replicate the Chef server deployment process or consider containerized deployment

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible assertions)
4. **ssh_profile.rb** (convert InSpec compliance profile to Ansible checks)
5. **deploy-chef-server.sh** and **deploy-automate.sh** (convert to Ansible playbooks)

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification beyond potential refactoring for best practices.
2. The compliance testing currently performed by InSpec is still required after migration.
3. The deployment of Chef Automate and Chef Infra Server will be replaced with equivalent infrastructure, not eliminated entirely.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The migration will maintain the same level of security hardening present in the original code.
6. No additional features beyond what exists in the current repository are required.