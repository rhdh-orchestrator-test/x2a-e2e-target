# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance tests and Ansible playbooks that demonstrate how to use Chef InSpec alongside Ansible for compliance automation. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting InSpec tests to Ansible-compatible compliance checks while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed as it's a static content file.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native solutions:
  - For compliance testing: Use Ansible Lint for static analysis
  - For runtime verification: Use the `ansible.builtin.assert` module or Molecule for testing
  - For comprehensive compliance: Consider integrating with OpenSCAP or using Ansible collections for security compliance

- **Test Kitchen with Vagrant**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook that enforces TLSv1.2 and disables vulnerable protocols.
- **SSH Hardening**: The SSH root login compliance check needs to be converted to an equivalent Ansible check.
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely in the migrated solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods will require careful mapping of InSpec resources to Ansible modules.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules and use Ansible's assert module for verification.

- **Chef Automate Deployment**: The Chef Automate and Chef Infra Server deployment scripts need to be replaced with equivalent Ansible roles.
  - Mitigation: Research existing Ansible roles for deploying alternative compliance platforms or create custom roles for the specific requirements.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format and only need minor adjustments for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity as they involve replacing Chef-specific functionality with Ansible alternatives.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not to provide production-ready infrastructure code.
2. The InSpec tests are intended to verify the configurations applied by the Ansible playbooks.
3. The deployment scripts are examples and not used in production environments, as they contain hardcoded credentials.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
5. There is no requirement to maintain backward compatibility with Chef InSpec after migration.
6. The migration will focus on preserving functionality rather than maintaining the exact structure of the original repository.
7. No external data sources or complex state management is involved in the current implementation.