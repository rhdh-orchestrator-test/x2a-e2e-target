# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a single engineer to complete the migration, including testing and documentation.

**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but the integration with Chef InSpec for compliance testing requires careful consideration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Two options:
  1. Convert InSpec tests to Ansible assertions or custom modules
  2. Keep InSpec as a compliance tool and integrate it with Ansible using the `inspec` Ansible module

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source version of Ansible Tower)
  - Ansible Semaphore
  - GitLab CI/CD with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced
  - Consider adding modern cipher suites
  - Implement proper certificate management

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure root login is disabled
  - Maintain SSH hardening in the migrated Ansible playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 sets of credentials in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Integration**: Maintaining compliance testing capabilities while migrating to pure Ansible
  - Solution: Use the Ansible `inspec` module to run existing InSpec tests or convert tests to Ansible assertions

- **Chef Automate Replacement**: Finding an equivalent solution for Chef Automate's functionality
  - Solution: Implement Ansible Automation Platform or AWX with appropriate dashboards and reporting

- **Test Kitchen Replacement**: Ensuring proper testing of Ansible roles
  - Solution: Implement Ansible Molecule for testing with similar capabilities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Convert to Ansible roles with proper structure
   - Low risk, direct conversion

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - Either integrate with Ansible using the inspec module or convert to Ansible assertions
   - Medium complexity due to testing framework differences

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Convert to Ansible playbooks for infrastructure deployment
   - Higher complexity due to the need to replace Chef Automate/Infra Server functionality

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool
2. Compliance testing is still a requirement, but can be implemented using Ansible or integrated InSpec
3. The Chef Automate/Infra Server deployment scripts are used for setting up the infrastructure management platform, which will be replaced by an Ansible-based solution
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The existing SSL/TLS security configurations should be maintained or improved
6. The migration will preserve all current functionality while eliminating dependencies on Chef
7. Test Kitchen is currently used only for development/testing and not in production pipelines