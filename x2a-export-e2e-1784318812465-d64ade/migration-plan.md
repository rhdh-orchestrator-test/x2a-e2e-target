# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small with two main components that need to be consolidated into a pure Ansible solution. The estimated timeline is 1-2 weeks for a single engineer due to the small codebase size and well-structured code.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with Chef InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Use Ansible's `assert` module for basic testing
  - Integrate with Molecule for more comprehensive testing
  - Use ansible-lint for static analysis and best practices enforcement

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for orchestration and management

### Security Considerations

- **SSL Configuration**: The playbooks include SSL hardening (disabling SSLv3, enabling TLSv1.2)
  - Migration approach: Preserve the same SSL hardening configurations in the Ansible playbooks

- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Convert InSpec SSH tests to Ansible assertions or include the `ansible-lockdown` security roles

- **Vault/secrets management**: For each module, identified credential patterns:
  - setup-automate: 3 credentials (username, password, organization name) - move to Ansible Vault
  - chef-and-ansible: 0 hardcoded credentials (certificates generated dynamically)

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation strategy: Map InSpec resources to equivalent Ansible modules and use assert or community testing modules

- **Chef Deployment Automation**: Replacing Chef Automate/Infra Server deployment with equivalent Ansible functionality
  - Mitigation strategy: Determine if Chef infrastructure is still needed or if it can be replaced with Ansible AWX/Tower

### Migration Order

1. **Ansible Playbooks** (low risk, high value)
   - Migrate `website_https.yml` and `poodle_fix.yml` to the new Ansible structure

2. **Testing Framework** (moderate complexity)
   - Convert InSpec tests to Ansible-native testing solutions
   - Replace Test Kitchen with Molecule for testing infrastructure

3. **Chef Deployment Scripts** (high complexity, dependencies)
   - Convert Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
   - Or replace with Ansible AWX/Tower deployment if Chef is no longer needed

### Assumptions

1. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible, not for testing Chef-managed infrastructure
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which may or may not be needed in the new Ansible-only environment
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
4. The migration will preserve all security hardening measures present in the original codebase
5. No external data sources or integrations are present beyond what's visible in the codebase
6. The Vagrant/Test Kitchen setup is primarily for development and testing, not production deployment