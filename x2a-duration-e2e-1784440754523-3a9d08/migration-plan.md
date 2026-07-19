# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration to mitigate POODLE vulnerability. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible testing framework or maintaining InSpec for testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible testing framework or maintaining InSpec for testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for deployment management.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for deployment management.

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a complementary testing tool
- **Test Kitchen**: Replace with Ansible-native testing solutions like Molecule
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for enterprise management or other Ansible-compatible CI/CD solutions

### Security Considerations

- SSL/TLS configuration: Maintain the security hardening present in the poodle_fix.yml playbook
- Self-signed certificates: Ensure proper certificate management in the migrated Ansible roles
- SSH security compliance: Preserve the SSH hardening checks from the InSpec profile
- Credentials management:
  - Hardcoded credentials in setup scripts (username, password, email)
  - Count: 2 scripts with hardcoded credentials
  - Type: Plain text passwords in bash scripts

### Technical Challenges

- **Compliance Testing**: Deciding whether to maintain Chef InSpec for compliance testing or migrate to Ansible-native testing solutions. Mitigation: Consider using Ansible Molecule with testinfra or maintaining InSpec as a complementary tool.
- **Infrastructure Management**: Replacing Chef Automate/Infra Server with Ansible-native management solutions. Mitigation: Evaluate Ansible AWX/Tower as a replacement or integrate with existing CI/CD pipelines.

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. Testing framework (kitchen.yml, InSpec tests) - Moderate complexity
3. Chef Automate/Infra Server deployment scripts - Higher complexity, requires architectural decisions

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, based on the README description.
2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible, not Chef.
3. The setup-automate scripts are used for deploying Chef Automate and Chef Infra Server, which would be replaced by Ansible AWX/Tower or other Ansible management solutions.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with proper secrets management in production.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.