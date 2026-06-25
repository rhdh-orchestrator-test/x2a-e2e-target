# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring a web server with HTTPS
2. Chef InSpec tests for validating compliance requirements
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting the InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for validating HTTPS configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH root login compliance check

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a test page for the web server. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule with Testinfra for more comprehensive testing
  - Option 4: Consider migrating to OpenSCAP or DISA STIG tools that integrate with Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLSv1.2 and disable older protocols. This security hardening should be preserved in the migration.
  - Migration approach: Maintain the same SSL/TLS configuration parameters in the Ansible playbooks

- **SSH Security**: The InSpec tests validate SSH root login restrictions.
  - Migration approach: Convert the InSpec SSH tests to equivalent Ansible assertions or Molecule/Testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Map each InSpec control to an equivalent Ansible assertion or Testinfra test

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef Automate and Chef Server deployment, or consider replacing with pure Ansible infrastructure

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests**: Convert to Ansible-compatible testing framework
3. **Chef Automate Deployment Scripts**: Convert to Ansible playbooks or replace with alternative infrastructure

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
3. The self-signed certificates are for demonstration purposes and may need to be replaced with proper certificate management in production.
4. The hardcoded credentials in the Chef Automate deployment scripts are for demonstration purposes and should be replaced with secure credential management.
5. The migration will focus on maintaining the same functionality while moving away from Chef-specific components.
6. The SSH compliance tests are generic enough to be applicable to the target environment without modification to the compliance requirements.