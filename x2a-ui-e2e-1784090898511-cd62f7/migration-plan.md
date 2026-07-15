# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and configuring Apache web servers with HTTPS
2. Chef InSpec tests for validating security compliance of the deployed infrastructure

The migration complexity is low to medium, as most of the configuration is already in Ansible format. The primary focus will be on replacing Chef InSpec tests with equivalent Ansible-native testing solutions. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server deployment with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website-https-compliance**:
    - Description: InSpec tests to validate HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

- **ssh-security-compliance**:
    - Description: InSpec tests to validate SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used as a test page for the web server. Can be directly used in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Server**: The deployment scripts suggest this environment was used for compliance reporting
  - Replace with Ansible AWX/Tower for centralized management
  - Consider integrating with compliance tools like OpenSCAP or Ansible's built-in security automation

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols
  - Migration approach: Maintain the same security settings but update to include TLS 1.3 if target systems support it
  - Consider using the `community.crypto` collection for certificate management

- **SSH Security**: InSpec tests validate SSH root login restrictions
  - Migration approach: Create equivalent Ansible tasks to validate and enforce SSH security settings
  - Use Ansible's `lineinfile` or `template` modules to manage SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using Ansible Vault for private keys
  - Document count: 2 sets of credentials in setup scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's `assert` module with appropriate conditionals to replicate InSpec tests
  - Example: For port checks, use Ansible's `wait_for` module before assertions

- **Compliance Metadata**: InSpec tests include rich compliance metadata (STIG IDs, CCI references)
  - Mitigation: Store compliance metadata in Ansible variables or as task tags/comments
  - Consider using Ansible's `documentation` keyword for structured documentation

- **Test Kitchen Integration**: Current setup uses Test Kitchen to orchestrate testing
  - Mitigation: Replace with Molecule and document the new testing workflow
  - Create equivalent Molecule scenarios for each Test Kitchen suite

### Migration Order

1. **website-https** and **poodle-fix** playbooks (low risk, already in Ansible format)
   - Review and update to current Ansible best practices
   - Consolidate into a single playbook with roles if appropriate

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule verifiers
   - Maintain compliance metadata in comments or variables

3. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible roles for infrastructure management
   - Replace Chef-specific functionality with Ansible equivalents

### Assumptions

1. The current setup uses Chef InSpec primarily for testing/validation, not for active configuration management
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. The security requirements (TLS 1.2, SSH restrictions) will remain the same
5. The Chef Automate/Server deployment scripts are included for reference but may not be actively used
6. No external data sources or dynamic inventory are being used
7. No complex secrets management is currently implemented
8. The Apache configuration is relatively standard and doesn't include custom modules or configurations
9. The self-signed certificates are for testing only and would be replaced in production