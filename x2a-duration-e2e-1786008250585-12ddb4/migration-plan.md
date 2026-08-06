# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance checks, STIG validation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a test page for the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Migrate to Ansible's built-in `assert` module for simple tests
  - Option 2: Use Molecule for Ansible role testing with testinfra as the verifier
  - Option 3: Keep InSpec but run it through Ansible rather than Chef

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

- **Vagrant (latest)**: Can be retained as Molecule supports Vagrant drivers

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should preserve the security hardening that disables SSLv3 and enables only TLSv1.2.
  - Migration approach: Convert to Ansible roles with the same security parameters

- **SSH Hardening**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create equivalent tests using Ansible's assert module or Molecule with testinfra

- **Credentials Management**: 
  - The deployment scripts contain hardcoded credentials (username, password) that should be moved to Ansible Vault
  - Count of credentials detected: 
    - automate-deployment: 4 (username, longusername, useremail, userpassword)
    - chef-server-deployment: 4 (username, longusername, useremail, userpassword)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks may require learning new testing methodologies.
  - Mitigation: Use Molecule with testinfra which has similar syntax to InSpec, or consider keeping InSpec as a testing tool even after migrating to Ansible

- **Chef Automate Deployment**: The Chef Automate and Chef Server deployment scripts need to be completely rewritten as Ansible roles.
  - Mitigation: Create Ansible roles that perform the same server setup and configuration steps

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Convert to a proper Ansible role structure
   - Add documentation

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Convert to a proper Ansible role structure
   - Add documentation

3. **InSpec tests** (moderate complexity)
   - Convert to Molecule/testinfra tests or Ansible assert tasks
   - Ensure they validate the same security and functionality aspects

4. **Chef deployment scripts** (high complexity)
   - Create Ansible roles to replace the bash scripts for Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential management

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, as indicated by the README mentioning it's companion code to a white paper.

2. The existing Ansible playbooks are functional and follow best practices, so they only need structural reorganization rather than logic changes.

3. There is no requirement to maintain backward compatibility with Chef InSpec after migration.

4. The deployment scripts for Chef Automate and Chef Server will be replaced with equivalent Ansible roles, as maintaining Chef infrastructure would be counterproductive in an Ansible migration.

5. The target environment will continue to be Ubuntu 20.04 as specified in the kitchen.yml file.

6. The migration will include improving security practices by moving hardcoded credentials to Ansible Vault.