# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of Ansible playbooks with Chef InSpec tests and Chef Automate/Chef Server deployment scripts. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec_compliance_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH root login security check

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Sample HTML file used for testing web server deployment. Migration consideration: Keep as-is or update as needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert module or migrate to Molecule for testing
  - Alternative: Keep InSpec as a standalone tool and call it from Ansible using the command module

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace with Ansible Automation Platform or alternative CI/CD solutions:
  - For configuration management: Use pure Ansible
  - For compliance reporting: Use AWX/Tower with ansible-lint or OpenSCAP integration
  - For user management: Use AWX/Tower role-based access control

### Security Considerations

- **SSL/TLS Configuration**: The current implementation properly disables SSLv3 and enables only TLSv1.2. Ensure this security hardening is maintained in the migrated solution.
  
- **SSH Security**: The InSpec profile checks for SSH root login being disabled. Ensure this security check is maintained using Ansible's assert module or ansible-lint.

- **Self-signed Certificates**: The current implementation generates self-signed certificates. Consider enhancing security by integrating with Let's Encrypt for production environments.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods may require additional modules or custom scripts. Mitigation: Use Ansible's uri module for HTTP checks and command module with OpenSSL for SSL verification.

- **Chef Server Functionality**: If Chef Server is being used for node management, this functionality will need to be replaced with Ansible inventory management. Mitigation: Implement dynamic inventory scripts or integrate with AWX/Tower.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing methods)
4. **Chef Deployment Scripts** (high complexity, requires replacement with Ansible Automation Platform deployment)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning it's related to content created by Technical Product Marketing.

2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible, not for verifying Chef-managed infrastructure.

3. The setup-automate scripts are used for setting up a Chef environment for testing or demonstration, not as part of the core infrastructure being managed.

4. The migration target is pure Ansible without any Chef components, including replacing InSpec with Ansible-native testing solutions.

5. The current implementation uses self-signed certificates for demonstration purposes, and the migration should maintain this approach unless otherwise specified.

6. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.