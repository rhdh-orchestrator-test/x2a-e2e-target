# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components, primarily focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting of two main components: 
1. Ansible playbooks for configuring a secure web server with SSL
2. Chef Automate/Chef Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The primary focus will be on standardizing the compliance testing approach within pure Ansible while preserving the security validation capabilities currently provided by Chef InSpec.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **secure-web-server**:
    - Description: Apache web server with SSL configuration, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **ssl-poodle-fix**:
    - Description: Security patch for Apache to mitigate POODLE vulnerability by disabling SSLv3 and enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script for Chef deployment
    - Key Features: User and organization creation, system configuration for Chef Automate

- **chef-server-deployment**:
    - Description: Deployment script for standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script for Chef deployment
    - Key Features: User and organization creation, system configuration for Chef Server

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec tests for validating HTTPS configuration and website functionality
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen with Vagrant**: Replace with:
  - Ansible Molecule for local testing
  - CI/CD pipeline integration for automated testing

- **Chef Automate/Server**: Replace Chef server deployment with:
  - Ansible AWX/Tower deployment playbooks
  - Ansible content collections management

### Security Considerations

- **SSL/TLS Configuration**: Preserve the security hardening in the Apache configuration
  - Maintain TLSv1.2 requirement and SSLv3 disablement
  - Ensure proper certificate management in the Ansible playbooks

- **SSH Hardening**: Maintain the SSH security controls currently validated by InSpec
  - Convert the InSpec SSH profile to Ansible security role or include in existing security role
  - Implement equivalent checks for root login restrictions

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec with Ansible-native testing
  - InSpec provides declarative compliance testing that needs to be replicated
  - Solution: Use Ansible assert modules or integrate with a compliance framework like OpenSCAP

- **Certificate Management**: The current solution generates self-signed certificates
  - Ensure proper certificate management in Ansible
  - Consider integrating with external certificate management systems if needed

- **User Management**: The Chef server scripts create users and organizations
  - Implement equivalent user management in Ansible AWX/Tower
  - Ensure proper credential storage and management

### Migration Order

1. **secure-web-server** (Priority 1): Already in Ansible format, minimal changes needed
2. **ssl-poodle-fix** (Priority 1): Already in Ansible format, minimal changes needed
3. **InSpec Tests** (Priority 2): Convert to Ansible-native testing framework
4. **chef-automate-deployment** and **chef-server-deployment** (Priority 3): Replace with Ansible AWX/Tower deployment

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes rather than production deployment
2. The InSpec tests are essential for compliance validation and must be preserved in functionality
3. The Chef Automate/Server deployment scripts are used for setting up a test environment
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data persistence or state management requirements
7. No specific performance requirements for the web server configuration
8. The self-signed certificates are acceptable (not requiring integration with a certificate authority)
9. No specific backup or disaster recovery requirements
10. The migration will maintain the same level of security hardening present in the original configuration