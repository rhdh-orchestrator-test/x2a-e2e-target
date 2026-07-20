# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL compliance
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration will require converting to Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be directly reused in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security hardening. Can be directly reused in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Will need to be converted to Ansible testing framework or kept as InSpec.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Will need to be converted to Ansible testing framework or kept as InSpec.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Will need to be converted to Ansible roles for infrastructure management.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Server deployment. Will need to be converted to Ansible roles for infrastructure management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with either:
  1. Continue using InSpec as a standalone tool called from Ansible
  2. Replace with Ansible-native testing using ansible-test or Molecule
  3. Replace with alternative compliance tools like OSCAP or Lynis

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  1. Ansible AWX/Tower for orchestration and management
  2. GitLab CI/CD or other CI/CD tools for pipeline automation
  3. Compliance reporting tools like Prometheus/Grafana for metrics

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening configurations in the poodle_fix.yml playbook
- **SSH Security**: The SSH compliance profile must be converted to equivalent Ansible security checks
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates and keys should be managed securely through Ansible Vault or external secret management
  - Count of credentials detected: 3 (username, password, SSL key)

### Technical Challenges

- **Compliance Testing**: Determining whether to keep InSpec or migrate to Ansible-native testing will be a key decision point. InSpec provides rich compliance testing capabilities that may be difficult to fully replicate in Ansible.
  - Mitigation: Consider keeping InSpec as a standalone tool called from Ansible playbooks for compliance testing.

- **Infrastructure Deployment**: The Chef Automate and Chef Infra Server deployment scripts need to be replaced with equivalent Ansible roles.
  - Mitigation: Create Ansible roles that perform the same system configurations and deployments as the bash scripts.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Testing Framework** (Moderate complexity)
   - Convert Test Kitchen to Molecule
   - Decide on compliance testing approach (keep InSpec or migrate)

3. **Chef Infrastructure** (High complexity)
   - Create Ansible roles to replace Chef Automate and Chef Infra Server deployment scripts
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining the compliance testing capabilities
2. The InSpec tests are valuable and should be preserved in some form
3. The deployment scripts are used for setting up infrastructure and can be replaced with Ansible roles
4. No actual Chef cookbooks or recipes are present in the repository that need migration
5. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migration
7. The repository is primarily for demonstration/educational purposes rather than production use