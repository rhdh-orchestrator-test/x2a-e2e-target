# MIGRATION FROM CHEF INSPEC AND BASH TO ANSIBLE

## Executive Summary

This repository contains Chef InSpec tests integrated with Ansible playbooks for compliance testing and configuration management, along with Bash scripts for Chef Automate and Chef Infra Server deployment. The migration scope involves converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving existing Ansible playbooks, and converting Bash deployment scripts to Ansible playbooks.

**Estimated Timeline**: 2-3 weeks
- Week 1: Convert InSpec tests to Ansible testing frameworks
- Week 2: Convert Chef deployment scripts to Ansible playbooks
- Week 3: Testing and documentation

**Complexity**: Medium - The repository contains a mix of technologies that require different migration approaches.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment with Apache, SSL/TLS compliance testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Molecule for Ansible role testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website with Apache. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality and security. Needs migration to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs migration to Ansible-compatible testing framework.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment. Can be preserved as-is.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on cloud VMs (based on comments in the deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - **Option 1**: Use Ansible's built-in `assert` module for basic testing
  - **Option 2**: Use Molecule for more comprehensive testing
  - **Option 3**: Integrate with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles
  - Supports multiple providers (Docker, Vagrant, etc.)
  - Integrates with various testing frameworks

- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX or other Ansible management platforms
  - Ansible Tower/AWX provides web UI, REST API, and role-based access control
  - Supports job scheduling, inventory management, and credential management
  - Offers dashboard and reporting features similar to Chef Automate

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL/TLS security testing and configuration. Ensure these security controls are maintained in the Ansible migration:
  - Disabling insecure protocols (SSL3)
  - Enabling secure protocols (TLS 1.2)
  - Certificate generation and management
  - Migration approach: Use Ansible's `openssl_*` modules as already demonstrated in the existing playbooks

- **SSH Security**: The repository includes SSH security testing. Ensure these security controls are maintained:
  - Root login restrictions
  - SSH configuration hardening
  - Migration approach: Use Ansible's `lineinfile` or `template` modules to manage SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: jtonello, password: password)
  - SSL/TLS certificate references
  - Recommend using Ansible Vault for securing these credentials
  - Count of credentials detected: 2 sets of credentials in deployment scripts

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing methodologies and syntax.
  - Mitigation: Start with simple assertions and gradually build more complex tests.
  - Example: Convert InSpec's `describe port(443) { it { should be_listening } }` to Ansible's `wait_for` module or Molecule's verifier.

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality in the Ansible ecosystem.
  - Mitigation: Evaluate Ansible Tower/AWX or other Ansible management platforms based on specific requirements.
  - Consider which Chef Automate features are actually needed (compliance reporting, visualization, etc.)

- **System Requirements**: The Chef deployment scripts set specific system parameters that need to be replicated in Ansible.
  - Mitigation: Use Ansible's `sysctl` module to set the same system parameters.
  - Example: Convert `sysctl -w vm.max_map_count=262144` to Ansible's sysctl module.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format):
   - `website_https.yml` - Apache HTTPS website deployment
   - `poodle_fix.yml` - SSL vulnerability fix

2. **InSpec Tests** (Medium complexity):
   - `website_https_verify.rb` - HTTPS functionality and security tests
   - `ssh_profile.rb` - SSH security compliance tests

3. **Chef Deployment Scripts** (Higher complexity):
   - `deploy-chef-server.sh` - Chef Infra Server deployment
   - `deploy-automate.sh` - Chef Automate and Chef Infra Server deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The existing Ansible playbooks are functioning correctly and don't require significant modifications.
3. There are no additional Chef cookbooks or resources not visible in the repository structure.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migration.
6. The team has experience with Ansible but may need training on Ansible testing frameworks to replace InSpec.
7. The migration will not require maintaining backward compatibility with Chef InSpec or Chef Automate.
8. The Apache web server configuration will remain similar in the migrated solution.