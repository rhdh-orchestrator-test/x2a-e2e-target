# MIGRATION FROM ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The repository also includes bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on maintaining the existing Ansible playbooks while potentially enhancing them with additional Ansible best practices and converting the Chef InSpec tests to Ansible-native testing solutions.

**Timeline Estimate**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen-ansible)**: Replace with Ansible Molecule for testing
- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible's assert module or Molecule's verify phase
  - For compliance testing: Consider migrating to OpenSCAP with Ansible or maintaining InSpec as a separate tool

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3 to mitigate POODLE vulnerability
  - Migration approach: Maintain the same security configurations but update to include TLS 1.3 if target systems support it
  
- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint to verify SSH security configurations

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Challenge 1**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule for more comprehensive testing
  
- **Challenge 2**: Migrating Chef Automate and Chef Server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment or consider if Chef components are still needed

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and update to follow Ansible best practices
   - Convert to role-based structure
   
2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and update to follow Ansible best practices
   - Consider merging with website_https role as a configuration option
   
3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   
4. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible roles if Chef components are still needed
   - Or document deprecation if moving entirely to Ansible

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. The Chef InSpec tests are used for compliance validation of Ansible-managed systems
3. The Chef Automate and Chef Server deployment scripts may not be needed if moving entirely to Ansible
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The security requirements (TLS 1.2, SSH hardening) will remain the same or be enhanced
6. Test Kitchen will be replaced with Ansible-native testing tools