# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing primarily on:

1. Preserving the compliance testing functionality currently provided by Chef InSpec
2. Consolidating the deployment and testing into a unified Ansible framework
3. Maintaining the security validation capabilities currently in place

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains relatively simple configurations but requires careful handling of compliance testing

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-deployment**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already)
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already)
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: Chef InSpec tests that validate HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS response validation, SSL/TLS protocol security checks

- **ssh-security-profile**:
    - Description: Chef InSpec profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards (STIG)

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Infra Server and Chef Automate
    - Path: setup-automate/deploy-chef-server.sh, setup-automate/deploy-automate.sh
    - Technology: Bash with Chef Server CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `index.html`: Sample HTML file for web server deployment
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Migrate to [ansible-lint](https://ansible-lint.readthedocs.io/) for static analysis
  - **Option 2**: Use [Molecule](https://molecule.readthedocs.io/) with testinfra for dynamic testing
  - **Option 3**: Implement custom Ansible tasks with assert modules to validate configurations

- **Test Kitchen**: Replace with Molecule for Ansible testing or maintain as is with Ansible provisioner

- **Chef Server/Automate**: The deployment scripts should be converted to Ansible roles for infrastructure deployment

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables vulnerable protocols (SSLv3) and enables only secure ones (TLSv1.2)
- **SSH Hardening**: The SSH security profile tests must be preserved in the Ansible-based solution
- **Self-signed Certificates**: The certificate generation process should be maintained or improved in the Ansible migration
- **Passwords in Scripts**: The Chef Server deployment scripts contain hardcoded passwords that should be moved to Ansible Vault in the migration

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation tasks will require careful mapping of test assertions
  - Mitigation: Use Ansible's assert module with appropriate conditions or integrate with testinfra
  
- **Compliance Reporting**: InSpec provides structured compliance reporting that needs to be replicated
  - Mitigation: Consider using Ansible callback plugins to generate structured reports or integrate with tools like AWX/Tower for reporting

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing
  - Mitigation: Replace with Molecule or adapt the existing kitchen.yml to work with the migrated solution

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and only need minor adjustments to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing approaches
3. **Chef Server Deployment Scripts**: Convert these bash scripts to Ansible roles and playbooks
4. **Test Kitchen Configuration**: Replace with Molecule or adapt for the new testing approach

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. The security requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution
4. The Chef Server deployment scripts are examples and not actively used in production
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The migration should preserve the educational/demonstration value of showing how compliance testing works with infrastructure deployment