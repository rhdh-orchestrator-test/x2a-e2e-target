# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with Ansible-native testing framework or adapting to use Ansible Molecule.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a complementary testing tool
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks for infrastructure deployment

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening for SSL/TLS protocols (specifically disabling SSLv3 and enabling TLSv1.2)
- **SSH Security**: The SSH security compliance checks must be preserved in the Ansible implementation
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely through Ansible Vault or other secret management solution

### Technical Challenges

- **Compliance Testing**: Deciding whether to maintain Chef InSpec for compliance testing or migrate to Ansible-native testing solutions
- **Infrastructure Deployment**: Converting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
- **Test Framework**: Replacing Test Kitchen with Ansible Molecule or another Ansible-native testing framework

### Migration Order

1. Ansible Playbooks (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml) - low risk, already in Ansible format
2. Compliance Testing (chef-and-ansible/tests/) - moderate complexity, requires decision on testing framework
3. Infrastructure Deployment Scripts (setup-automate/) - higher complexity, requires converting bash scripts to Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible for compliance automation, not for production deployment
2. The hardcoded credentials in the setup scripts are for demonstration purposes only
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The migration will standardize on Ansible while potentially maintaining InSpec for compliance testing
5. The repository is primarily educational/demonstrational rather than a production infrastructure codebase
6. The SSL/TLS security configurations are critical to maintain in the migration
7. The deployment scripts are designed for both on-premises and cloud environments
8. There are no external dependencies or integrations beyond what's explicitly defined in the repository