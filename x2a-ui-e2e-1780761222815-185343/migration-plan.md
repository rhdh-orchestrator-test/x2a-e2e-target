# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on two Ansible playbooks and associated InSpec tests, plus Chef Automate/Chef Server deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS website deployment and security configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for website deployment testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Option 1: Use Ansible's built-in assert module for basic validation
  - Option 2: Integrate with Molecule for testing Ansible roles
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Keep InSpec as a separate validation tool but manage its installation via Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or Ansible's own testing frameworks

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Ensure the Ansible playbook continues to enforce strong TLS configuration

- **SSH Security**: The InSpec test validates SSH root login security
  - Approach: Create equivalent Ansible assertions or continue using InSpec for validation

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Approach: Maintain the same approach or enhance with Let's Encrypt integration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Recommendation: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Create equivalent assertions using Ansible's assert module or maintain InSpec as a separate validation tool

- **Compliance Metadata**: The InSpec tests include rich compliance metadata (STIG, CCI references)
  - Mitigation: Ensure this metadata is preserved in comments or documentation if moving away from InSpec

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Replace with Molecule or another Ansible-native testing framework

### Migration Order

1. **website_https.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure if appropriate

2. **poodle_fix.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https role if appropriate

3. **InSpec Tests** (moderate complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native testing)
   - Implement chosen testing approach

4. **Chef Automate/Server Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible roles for deploying infrastructure
   - Replace hardcoded credentials with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies where possible
2. InSpec tests may need to be preserved for compliance reasons or converted to equivalent Ansible validation
3. The deployment scripts for Chef Automate/Server may be obsolete if the goal is to move away from Chef entirely
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The security requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution
6. Test Kitchen integration is not required in the final solution if replaced with Ansible-native testing
7. The self-signed certificate approach is acceptable for the migrated solution
8. No external dependencies or integrations beyond what's visible in the repository need to be considered