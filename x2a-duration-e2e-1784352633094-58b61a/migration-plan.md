# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations with a focus on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** as most of the content is already in Ansible format, with the primary work being to integrate the InSpec testing functionality into native Ansible testing frameworks. Estimated timeline: **1-2 weeks** for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec testing for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible Molecule or similar Ansible-native testing framework.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Can be directly reused in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be directly reused in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be migrated to Ansible-native testing (Molecule, testinfra, or Ansible assert).
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Should be migrated to Ansible-native testing or integrated with Ansible security roles.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Should be replaced with Ansible roles for configuration management server deployment.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Should be replaced with Ansible roles for configuration management server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in setup-automate script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing frameworks:
  - Option 1: Use Ansible Molecule for testing infrastructure
  - Option 2: Use testinfra (Python-based testing framework compatible with Ansible)
  - Option 3: Use Ansible assert modules and custom modules for compliance testing

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise Ansible management
  - Option 2: Ansible Semaphore for lightweight Ansible UI
  - Option 3: GitLab CI/CD pipelines for Ansible execution

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security configuration:
  - Maintain TLSv1.2 requirement and disable older protocols
  - Consider upgrading to TLSv1.3 where supported
  - Implement certificate management via Ansible vault or external secret management

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Implement equivalent compliance checks using Ansible or compatible tools

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate generation should use Ansible Vault for key storage or integrate with external certificate management

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec with equivalent Ansible-native testing capabilities:
  - Challenge: InSpec provides a domain-specific language for compliance testing that is more readable than raw Ansible
  - Mitigation: Use a combination of Ansible assert modules, custom modules, and potentially integrate with tools like OSCAP

- **Certificate Management**: The current solution generates self-signed certificates:
  - Challenge: Enterprise environments typically require proper certificate management
  - Mitigation: Integrate with certificate authorities or implement Let's Encrypt support in the Ansible roles

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml)
   - Low risk as they are already in Ansible format
   - May need minor updates to follow current Ansible best practices

2. **Testing Framework** (chef-and-ansible/tests/*)
   - Moderate complexity to replace InSpec with Ansible-native testing
   - Create equivalent tests using Ansible Molecule or testinfra

3. **Chef Server Deployment** (setup-automate/*)
   - Higher complexity to replace with Ansible roles for configuration management
   - Requires decisions on which Ansible management platform to use

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.md mentioning it's related to content created by Technical Product Marketing.

2. The Chef InSpec tests are the primary value in the repository, as they demonstrate compliance automation alongside Ansible.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the scripts mention they can work on cloud VMs as well.

4. The migration will maintain the same functionality but standardize on Ansible-only tools rather than the current hybrid approach.

5. Self-signed certificates are acceptable for the demonstration environment, but production migrations might require integration with proper certificate authorities.

6. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with proper secret management in a production environment.