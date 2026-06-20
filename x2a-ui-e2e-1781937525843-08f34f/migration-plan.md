# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used for compliance automation alongside Ansible deployments. The migration scope is relatively small, focusing on two main Ansible playbooks and associated InSpec tests. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for website deployment testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Option 1: Use Ansible's built-in `assert` module for basic validation
  - Option 2: Integrate with Molecule for testing
  - Option 3: Convert InSpec tests to Ansible roles that perform the same validation checks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines (GitHub Actions, GitLab CI, etc.)

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Convert the poodle_fix.yml playbook to an Ansible role with appropriate handlers

- **SSH Security**: The SSH root login check needs to be maintained
  - Approach: Convert the InSpec test to an Ansible task that validates the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated in the website_https.yml playbook
  - Recommendation: Use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Create custom Ansible modules or use assert module with appropriate conditions
  
- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI references)
  - Mitigation: Store compliance metadata in Ansible role variables or as comments in tasks

- **Certificate Management**: The current solution generates self-signed certificates
  - Mitigation: Create an Ansible role for certificate management that can handle both self-signed and proper CA certificates

### Migration Order

1. **website_https.yml** (Priority 1): Already in Ansible format, just needs reorganization into proper role structure
2. **poodle_fix.yml** (Priority 1): Already in Ansible format, can be integrated into the website_https role
3. **InSpec Tests** (Priority 2): Convert to Ansible assertions or Molecule tests
4. **Chef Automate Deployment Scripts** (Priority 3): Convert bash scripts to Ansible roles for Chef infrastructure deployment

### Assumptions

1. The primary goal is to migrate all functionality to pure Ansible without Chef InSpec dependency
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. Self-signed certificates are acceptable for the web server configuration
5. The Chef Automate and Chef Server deployment scripts may be deprecated if the organization is fully migrating to Ansible
6. The security compliance requirements (STIG, CCI) need to be maintained in the Ansible implementation
7. No external data sources or dynamic inventory are being used in the current implementation