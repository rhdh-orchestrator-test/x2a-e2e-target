# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving Chef Automate and Chef Infra Server deployment scripts, along with InSpec tests that are already designed to work with Ansible playbooks. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited Chef-specific components.

## Module Migration Plan

This repository contains Chef deployment scripts and InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User creation, organization setup, server configuration, system tuning (vm.max_map_count, vm.dirty_expire_centisecs)

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for compliance verification of web servers and SSH
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL/TLS protocol validation, SSH security compliance checks with CCI/STIG references

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server with Apache2, SSL certificates, and virtual hosts. Migration consideration: Already in Ansible format, can be used as-is.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability by enforcing TLSv1.2. Migration consideration: Already in Ansible format, can be used as-is.
- `chef-and-ansible/index.html`: Simple HTML template for testing web server deployment. Migration consideration: Can be used as-is or templated with Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Replace with Ansible playbook for configuration management.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Replace with Ansible playbook for configuration management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (as mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Can be retained as a compliance testing tool that works with Ansible, or replaced with Ansible-native alternatives like:
  - ansible-lint for static code analysis
  - Molecule for testing Ansible roles
  - OpenSCAP integration for compliance scanning

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS hardening (POODLE vulnerability fix). Ensure these security configurations are maintained in the Ansible migration.
- **SSH Security Controls**: InSpec tests verify SSH root login is disabled. Maintain these security checks in the Ansible migration.
- **Self-signed Certificates**: The Ansible playbooks generate self-signed certificates. Consider implementing a more robust certificate management solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: 'jtonello', password: 'password') should be migrated to Ansible Vault
  - SSL/TLS certificate references in the Ansible playbooks should use secure storage
  - Count of credentials detected: 2 sets of credentials in each deployment script (username/password and organization name/description)

### Technical Challenges

- **InSpec Integration**: Determining whether to keep InSpec for compliance testing or migrate to an Ansible-native solution. Mitigation: InSpec can continue to work with Ansible, so this could be a phased approach.
- **Configuration Management**: Replacing the Chef server deployment with equivalent Ansible roles. Mitigation: Use community-maintained Ansible roles for configuration management or develop custom roles.
- **System Tuning**: The Chef deployment scripts set specific kernel parameters that need to be maintained in the Ansible migration. Mitigation: Use Ansible's sysctl module to apply the same configurations.

### Migration Order

1. **Ansible Playbooks** (already in Ansible format, no migration needed)
   - website_https.yml
   - poodle_fix.yml

2. **Chef Deployment Scripts** (convert to Ansible playbooks)
   - deploy-chef-server.sh
   - deploy-automate.sh

3. **Testing Framework** (evaluate options)
   - Keep InSpec tests as-is since they work with Ansible
   - Or migrate to Ansible-native testing frameworks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The InSpec tests are intended to remain as compliance verification tools even after migration to Ansible.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The repository is not a complete Chef cookbook but rather examples of Chef components working alongside Ansible.
6. The migration will maintain the same level of security compliance as demonstrated in the InSpec tests.
7. The deployment scripts are intended for lab environments as indicated by the domain names and organization names used.