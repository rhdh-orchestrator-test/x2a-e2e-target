# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for secure website deployment
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing with InSpec

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website with HTTPS. Can be directly incorporated into the Ansible collection.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be directly incorporated into the Ansible collection.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be migrated to Ansible test framework or kept as InSpec.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Should be migrated to Ansible test framework or kept as InSpec.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be replaced with Ansible roles for configuration management platform deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be replaced with Ansible roles for configuration management platform deployment.

### Target Details

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing frameworks like Molecule or maintain InSpec as a complementary testing tool
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible management solution

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure SSL for web servers with specific security settings (disabling SSLv3, enabling TLSv1.2). These security configurations must be preserved in the migrated Ansible roles.
- **SSH Security**: The InSpec profile checks for SSH root login restrictions. This compliance check should be maintained in the Ansible testing framework.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider implementing proper certificate management in the migrated solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate and key files

### Technical Challenges

- **Compliance Testing**: Deciding whether to maintain Chef InSpec for compliance testing or migrate to an Ansible-native solution. InSpec provides robust compliance testing capabilities that may be challenging to replicate with Ansible alone.
- **Testing Framework**: Replacing Test Kitchen with Molecule will require adapting the testing workflow and potentially rewriting test assertions.
- **Configuration Management Platform**: Replacing Chef Automate/Infra Server with an Ansible management solution will require evaluating requirements for centralized configuration management.

### Migration Order

1. Ansible Playbooks (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml) - Low risk, already in Ansible format
2. Testing Framework (chef-and-ansible/kitchen.yml) - Moderate complexity, requires adapting to Molecule
3. Compliance Tests (chef-and-ansible/tests/*.rb) - Moderate complexity, requires decision on testing approach
4. Chef Deployment Scripts (setup-automate/*.sh) - High complexity, requires replacing with Ansible roles

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the same functionality and security posture.
2. Chef InSpec may be retained as a compliance testing tool if it provides capabilities not easily replicated in Ansible.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible roles for deploying a configuration management platform.
4. The target environment will remain Ubuntu 20.04 or compatible Linux distributions.
5. The security requirements (SSL/TLS configurations, SSH hardening) will remain the same in the migrated solution.
6. The repository is primarily for demonstration purposes rather than production use, based on the README indicating it's for "working examples" related to content created by Technical Product Marketing.