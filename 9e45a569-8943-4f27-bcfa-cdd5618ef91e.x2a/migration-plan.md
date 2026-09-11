# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples for using Chef InSpec alongside Ansible for compliance automation, rather than traditional Chef cookbooks. The migration scope is limited as the repository already uses Ansible playbooks for infrastructure provisioning, with Chef InSpec providing compliance testing. The primary migration task involves replacing Chef InSpec tests with Ansible-native testing solutions.

**Migration Complexity**: Low  
**Estimated Timeline**: 1-2 weeks  
**Risk Level**: Low - No production cookbooks to migrate

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible demonstration playbooks that need migration planning:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS website deployment with SSL/TLS configuration and compliance verification using Chef InSpec
- Path: chef-and-ansible/
- Technology: Ansible playbooks with Chef InSpec testing
- Key Features: Apache 2.4 installation, self-signed SSL certificate generation, virtual host configuration, TLS 1.2 enforcement, compliance testing for HTTPS and SSH security

**chef-infrastructure-setup**:
- Description: Bash scripts for deploying Chef Automate and Chef Infra Server infrastructure
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification - needs migration to molecule or native Ansible testing
- `website_https.yml`: Ansible playbook for Apache HTTPS setup - already in target format, no migration needed
- `poodle_fix.yml`: Ansible playbook for SSL security hardening - already in target format, no migration needed
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality - needs migration to Ansible testing modules
- `tests/ssh_profile.rb`: Chef InSpec compliance profile for SSH security - needs migration to Ansible testing modules
- `deploy-automate.sh`: Chef infrastructure deployment script - may need conversion to Ansible playbook
- `deploy-chef-server.sh`: Chef server deployment script - may need conversion to Ansible playbook

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible testing modules (ansible.builtin.uri, ansible.builtin.wait_for, community.crypto.openssl_certificate_info)
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
- **Chef Automate/Server**: Evaluate if infrastructure deployment scripts should be converted to Ansible playbooks

### Security Considerations

- **SSL/TLS Configuration**: Current implementation uses self-signed certificates and enforces TLS 1.2 - migration should maintain these security standards
- **SSH Hardening**: InSpec tests verify SSH root login is disabled - equivalent Ansible assertions needed
- **Certificate Management**: Self-signed certificate generation is already handled by Ansible openssl modules - no migration needed
- **Compliance Testing**: Chef InSpec compliance profiles need conversion to Ansible testing tasks
- **Secrets Management**: No hardcoded credentials found in playbooks - deployment scripts contain example credentials that should be parameterized

### Technical Challenges

- **InSpec to Ansible Testing**: Converting Chef InSpec compliance tests to native Ansible testing requires rewriting test logic using Ansible modules like uri, wait_for, and assert
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test configuration and execution workflow
- **Compliance Reporting**: Chef InSpec provides detailed compliance reporting - need to implement equivalent reporting with Ansible testing modules
- **Infrastructure Scripts**: Bash scripts for Chef infrastructure deployment may need conversion to Ansible playbooks for consistency

### Migration Order

1. **Ansible Playbooks** (already complete - no migration needed)
   - website_https.yml and poodle_fix.yml are already in Ansible format
2. **InSpec Test Migration** (moderate complexity)
   - Convert website_https_verify.rb to Ansible testing tasks
   - Convert ssh_profile.rb to Ansible compliance assertions
3. **Test Framework Migration** (low complexity)
   - Replace Test Kitchen with Molecule configuration
4. **Infrastructure Scripts** (optional)
   - Convert deployment scripts to Ansible playbooks if desired

### Assumptions

- The primary goal is to eliminate Chef InSpec dependency while maintaining compliance testing capabilities
- Ansible testing modules (uri, wait_for, assert) can provide equivalent functionality to Chef InSpec tests
- Test Kitchen replacement with Molecule is acceptable for the testing workflow
- The existing Ansible playbooks are considered the target state and do not need modification
- Chef infrastructure deployment scripts may remain as bash scripts unless there's a specific requirement to convert them to Ansible
- The demonstration nature of this repository means production-grade error handling and edge cases may not be fully implemented
- SSL certificate validation and compliance checks need to maintain the same security standards as the current InSpec tests