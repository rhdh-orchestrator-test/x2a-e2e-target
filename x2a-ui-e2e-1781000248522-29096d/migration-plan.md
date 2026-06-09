# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used for compliance automation alongside Ansible deployments. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and securing Apache web servers
2. Chef InSpec tests for validating security compliance

The migration complexity is low to moderate, as most of the infrastructure code is already in Ansible format. The primary migration task will be to replace Chef InSpec tests with equivalent Ansible-native testing solutions. Estimated timeline: 1-2 weeks for a single developer.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server deployment with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security patch for Apache SSL configuration to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 protocol

- **website-https-compliance**:
    - Description: InSpec tests to validate HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security configuration validation
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script with Chef commands
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script with Chef commands
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for web server deployment testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Implement custom Ansible playbooks with assert modules for validation

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Server**: The deployment scripts for Chef infrastructure can be replaced with:
  - Ansible AWX/Tower deployment playbooks
  - Alternative compliance platforms like OpenSCAP

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enforces TLSv1.2
  - Migration approach: Preserve the same Apache configuration settings in the Ansible playbooks

- **SSH Security**: The SSH root login restrictions must be maintained
  - Migration approach: Create equivalent Ansible tasks to enforce SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

- **Self-signed certificates**: The current implementation generates self-signed certificates
  - Migration approach: Consider integrating with Let's Encrypt for production environments

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec's compliance testing capabilities
  - Mitigation: Evaluate Ansible Molecule, ansible-test, or other testing frameworks that can validate security configurations
  - Consider OpenSCAP integration for STIG compliance validation

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing
  - Mitigation: Replace with Ansible Molecule which provides similar functionality in an Ansible-native way

### Migration Order

1. **website-https** and **poodle-fix** Ansible playbooks (low risk, already in Ansible format)
   - Consolidate into a single playbook with proper role structure
   - Implement Ansible best practices (use of roles, variables, etc.)

2. **InSpec Tests** (moderate complexity)
   - Develop equivalent tests using Ansible Molecule or custom assert playbooks
   - Ensure all security checks are preserved

3. **Chef Automate/Server Deployment Scripts** (high complexity)
   - Replace with Ansible playbooks for deploying alternative infrastructure
   - Consider AWX/Tower or other compliance platforms

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The hardcoded credentials in the setup scripts are for demonstration purposes only
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The migration will need to maintain the same level of security validation currently provided by InSpec
5. No external dependencies or integrations beyond what's visible in the repository
6. The Apache configuration and security hardening requirements will remain the same
7. Test Kitchen is only used for development/testing and not for production deployments