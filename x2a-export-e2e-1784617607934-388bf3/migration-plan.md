# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The repository appears to be a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Consolidating the existing Ansible playbooks
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

Given the limited scope and small number of files, this migration is estimated to be low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks and Chef InSpec tests for web server configuration and compliance testing
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks and Chef InSpec tests)
    - Key Features: Apache HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Directory containing bash scripts for Chef Automate and Chef Server deployment
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling older SSL protocols and enabling only TLSv1.2.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test that verifies SSH root login is disabled according to security requirements.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS is properly configured on the web server.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier.
- `chef-and-ansible/index.html`: Simple HTML file used for testing the web server deployment.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP or DISA STIG Ansible roles

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Server**: Replace with Ansible Automation Platform or other Ansible management solutions

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migrated Ansible content.
  - Migration approach: Use the `community.general.apache2_module` and `ansible.builtin.lineinfile` modules to manage Apache SSL configuration.

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls and use Ansible's assert module to verify compliance.

- **Self-signed Certificates**: The playbook generates self-signed certificates for HTTPS.
  - Migration approach: Use Ansible's `community.crypto` collection for certificate management.

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef Server deployment scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault or integrate with a secrets management solution like HashiCorp Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests requires understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules and develop a testing framework that achieves the same compliance goals.

- **Chef Server Deployment**: Replacing the Chef Server deployment scripts with Ansible requires understanding the Chef Server architecture.
  - Mitigation: Create an Ansible role that installs and configures the necessary components or consider replacing with Ansible Automation Platform.

### Migration Order

1. **chef-and-ansible** (Priority 1): Review and optimize the existing Ansible playbooks, convert InSpec tests to Ansible-native testing solutions
2. **setup-automate** (Priority 2): Replace Chef Server deployment scripts with Ansible roles and playbooks

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment.
2. The InSpec tests are used for compliance validation of infrastructure configured by Ansible.
3. The Chef Server deployment scripts are used for setting up a Chef environment, which would be replaced by Ansible Automation Platform or similar.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no complex Chef cookbooks or recipes to migrate, only InSpec tests and bash scripts.
6. The security requirements (SSH hardening, TLS configuration) need to be maintained in the migrated solution.
7. The migration will consolidate all functionality into a single Ansible-based solution.