# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure web servers with HTTPS support
2. Chef InSpec tests used for compliance verification of Ansible-managed systems
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on standardizing the existing Ansible playbooks to follow best practices and migrating the Chef InSpec tests to Ansible-native testing frameworks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for infrastructure setup.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static code analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing:
  - Molecule provides similar functionality but is designed specifically for Ansible
  - Will require new molecule.yml configuration files

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles:
  - Create roles for infrastructure components
  - Use Ansible Vault for sensitive data currently in shell scripts

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration and POODLE vulnerability remediation:
  - Maintain the same security hardening in the migrated Ansible roles
  - Consider using the community.crypto collection for certificate management
  
- **Self-signed Certificates**: The current implementation uses self-signed certificates:
  - Consider integrating with Let's Encrypt for production environments
  - Use Ansible Vault for storing certificate private keys

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected (user credentials in both setup scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule verifiers:
  - Challenge: InSpec has specific SSL testing capabilities
  - Mitigation: Use the uri module with appropriate SSL parameters and custom verification scripts

- **Configuration Templates**: The current implementation uses inline templates in YAML:
  - Challenge: Maintaining readability with complex templates
  - Mitigation: Move to separate template files using Jinja2

### Migration Order

1. **website_https playbook** (low risk, high value):
   - Convert to Ansible role with proper directory structure
   - Move inline templates to separate files
   - Implement idempotency improvements

2. **poodle_fix playbook** (low complexity):
   - Integrate into the website_https role as a separate task file
   - Ensure handlers are properly consolidated

3. **InSpec tests** (moderate complexity):
   - Convert to Molecule tests or Ansible assertions
   - Ensure all compliance checks are maintained

4. **Chef Automate/Server deployment scripts** (high complexity):
   - Create Ansible roles for infrastructure setup
   - Implement Ansible Vault for credentials
   - Add idempotency to prevent redeployment issues

### Assumptions

1. The current Ansible playbooks are not organized according to Ansible best practices (roles, collections)
2. The InSpec tests are essential for compliance verification and must be maintained in some form
3. The Chef Automate and Chef Infra Server deployments are needed for the overall infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates are acceptable for the environment, or will be replaced with proper certificates
6. The hardcoded credentials in the setup scripts are for demonstration purposes only
7. The Apache version pinning (2.4.41-4ubuntu3.10) is intentional for compliance reasons