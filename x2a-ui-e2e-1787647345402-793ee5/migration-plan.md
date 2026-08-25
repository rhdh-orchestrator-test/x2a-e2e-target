# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be primarily educational in nature, showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec tests for verifying the configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully convert all components to pure Ansible solutions.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that checks SSH server configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML content for the website. Can be directly used in Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For website_https_verify.rb: Use Ansible URI module with assert for HTTP checks and community.crypto.openssl_certificate_info module for SSL verification
  - For ssh_profile.rb: Use ansible-lint security rules or OpenSCAP Ansible integration

- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with AWX/Ansible Tower or other Ansible management platform

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (currently done in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Implement certificate renewal automation

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Incorporate these checks into Ansible roles
  - Expand SSH hardening to include key-based authentication, protocol version restrictions, etc.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely or replaced with Let's Encrypt integration

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible assertions will require careful mapping of test logic
  - Mitigation: Use ansible.builtin.assert module combined with command/shell modules to replicate InSpec resource tests
  - Consider ansible-test or molecule verify for more complex test scenarios

- **Chef Server Deployment**: Replacing Chef Server deployment scripts with equivalent Ansible roles
  - Mitigation: Research existing Ansible Galaxy roles for similar functionality or create custom roles

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Add idempotency improvements if needed

2. **poodle-fix playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Consider merging with website-https as a single role with configurable options

3. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions
   - Convert ssh_profile.rb to Ansible security checks

4. **Chef deployment scripts** (high complexity)
   - Replace with Ansible roles for AWX/Tower deployment if needed
   - Or create documentation for alternative CI/CD approaches

### Assumptions

1. The repository is primarily educational/demonstrative and not used in production
2. The InSpec tests are used only for verification and not for continuous compliance
3. There are no external dependencies on Chef beyond what's visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The self-signed certificates are acceptable for the use case (not production)
6. The hardcoded credentials in scripts are for demonstration purposes only