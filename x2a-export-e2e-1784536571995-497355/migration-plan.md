# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-ssl-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-compliance**:
    - Description: Chef InSpec test profile that verifies HTTPS website functionality and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **ssh-security-compliance**:
    - Description: Chef InSpec test profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Server installation, user and organization creation

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file used in website deployment - can be preserved as-is or incorporated into Ansible templates

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native compliance testing using one of:
  - Ansible's built-in assert module for basic tests
  - Molecule for more comprehensive testing
  - Integration with other compliance tools like OSCAP or maintain InSpec as a standalone tool

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Either deploy alternative compliance platforms (AWX/Ansible Tower)
  - Or maintain the ability to deploy Chef Automate if it's still needed for compliance reporting

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain the same level of Apache security configuration

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Consider enhancing with Let's Encrypt integration for production environments
  - Ensure certificate permissions are properly set (mode 0640 as in original)

- **SSH Hardening**: Maintain compliance with the SSH security profile
  - Ensure root login remains disabled
  - Consider expanding SSH hardening based on the STIG references in the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **Compliance Testing**: The primary challenge will be replacing Chef InSpec tests with equivalent Ansible-based testing
  - InSpec provides a domain-specific language for compliance testing that's more expressive than basic Ansible assertions
  - Solution: Consider using Ansible Molecule with testinfra or maintaining InSpec as a standalone tool called from Ansible

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Solution: Replace with Molecule which is designed specifically for Ansible testing

- **Chef Server Deployment**: The deployment scripts for Chef Server will need complete replacement
  - Solution: Create Ansible playbooks that either deploy alternative infrastructure or maintain the ability to deploy Chef components if needed

### Migration Order

1. **website-https-configuration** (Priority 1, low risk)
   - Already an Ansible playbook, minimal changes needed
   - Focus on improving variable organization and template usage

2. **poodle-ssl-fix** (Priority 1, low risk)
   - Already an Ansible playbook, minimal changes needed
   - Consider merging with the website-https playbook for a comprehensive Apache security role

3. **chef-server-deployment** and **chef-automate-deployment** (Priority 2, moderate complexity)
   - Convert shell scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

4. **website-https-compliance** and **ssh-security-compliance** (Priority 3, high complexity)
   - Develop equivalent compliance testing in Ansible ecosystem
   - Consider maintaining InSpec as a standalone tool if direct conversion is too complex

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining the same level of compliance testing
2. Chef InSpec is currently being used primarily for its testing capabilities, not for configuration management
3. The deployment scripts for Chef Server and Automate are used for demonstration purposes and not critical production infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. The security compliance requirements (especially those referenced in the SSH profile with STIG IDs) must be maintained
7. No external data sources or complex variable structures are being used beyond what's visible in the repository