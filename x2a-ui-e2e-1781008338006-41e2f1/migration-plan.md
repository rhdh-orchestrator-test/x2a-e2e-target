# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS/SSL setup and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache virtual host configuration, SSL certificate generation, website deployment

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in SSL configurations
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website-https-compliance**:
    - Description: InSpec tests for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, CCI compliance mapping, STIG validation

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Approach: Create an Ansible role for Apache SSL hardening that implements the same security controls
  
- **SSH Hardening**: The SSH compliance profile needs to be converted to Ansible
  - Approach: Create an Ansible role that implements the same SSH security controls and adds assertions

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely through Ansible Vault or external certificate management

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible assertions
  - Mitigation: Use assert modules in Ansible or consider maintaining InSpec for testing while using Ansible for configuration

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible functionality
  - Mitigation: Determine if Chef server is still needed or if it can be replaced entirely with Ansible Automation Platform

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Refactor into proper Ansible role structure
   - Add documentation and variables

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Incorporate into the Apache/SSL role
   - Add conditional logic for different OS versions

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions where possible
   - For complex tests, maintain InSpec but integrate with Ansible workflow

4. **Chef Infrastructure Deployment** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If not, remove; if yes, create Ansible playbooks to deploy Chef infrastructure

### Assumptions

1. The primary goal is standardizing on Ansible while maintaining the same functionality
2. Chef InSpec tests may need to be preserved for their specific compliance capabilities
3. The Chef server deployment scripts may be obsolete if moving entirely to Ansible
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests must be maintained
7. No complex state management or database migrations are required