# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes scripts for setting up Chef Automate and Chef Infra Server environments.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The complexity is low to moderate, as we need to replace the InSpec testing functionality with Ansible-native solutions. Estimated timeline for migration is 1-2 weeks, with most of the effort focused on replacing the InSpec compliance testing with Ansible alternatives.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance checks

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Static HTML content for the web server. Can be directly migrated to Ansible template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic validation: Use Ansible's `assert` module and `register` functionality
  - For compliance testing: Consider using ansible-lint, OpenSCAP with Ansible, or Molecule for testing
  - For continuous compliance: Consider integrating with AWX/Tower for scheduled compliance checks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles
  - Can use the same Vagrant driver for local testing

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - AWX/Tower for job scheduling and reporting
  - OpenSCAP for compliance scanning
  - Prometheus/Grafana for metrics and visualization

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migrated Ansible roles.
  - Migration approach: Create an Ansible role for Apache with SSL hardening as a separate task file

- **SSH Hardening**: The InSpec tests validate SSH security configurations (disabling root login).
  - Migration approach: Create an Ansible role for SSH hardening that applies the same controls

- **Self-signed Certificates**: The playbook generates self-signed certificates for HTTPS.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) but consider adding proper certificate management

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Replacing InSpec Testing**: The primary challenge is replacing the InSpec testing functionality with Ansible-native solutions.
  - Mitigation: Use a combination of Ansible's `assert` module, `uri` module for HTTP testing, and custom modules or external tools for SSL validation

- **Compliance Reporting**: If compliance reporting is a requirement, finding an equivalent to Chef Automate's compliance reporting capabilities.
  - Mitigation: Consider integrating with AWX/Tower and OpenSCAP for compliance reporting

### Migration Order

1. **website_https.yml** (Priority 1): Core web server configuration playbook, already in Ansible format
   - Convert to an Ansible role with proper structure
   - Move variables to defaults/vars
   - Create templates for configuration files

2. **poodle_fix.yml** (Priority 1): Security hardening playbook, already in Ansible format
   - Integrate into the web server role as a security task

3. **InSpec Tests** (Priority 2): Replace with Ansible testing
   - Create equivalent tests using Ansible's assert module
   - Set up Molecule for test automation

4. **Chef Automate/Server Scripts** (Priority 3): Replace with Ansible AWX/Tower setup if needed
   - Create Ansible playbooks for equivalent functionality
   - Use Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used with Ansible for compliance automation, not for production deployment.

2. The InSpec tests are used for validation after Ansible playbook execution, and this validation capability needs to be preserved in the migration.

3. The Chef Automate and Chef Server setup scripts are included as examples and may not be central to the main functionality.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

5. There is no complex state management or data persistence requirements beyond the configuration files.

6. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with proper secret management in production.

7. The self-signed certificates are for demonstration purposes and would be replaced with proper certificates in production.