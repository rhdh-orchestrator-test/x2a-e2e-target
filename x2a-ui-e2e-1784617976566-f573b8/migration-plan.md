# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need to be consolidated into a unified Ansible approach. The repository appears to be a demonstration of using Chef InSpec for compliance testing with Ansible playbooks, along with scripts for deploying Chef infrastructure. The migration scope is relatively small, with only two Ansible playbooks and two Chef deployment scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (already in Ansible) and medium complexity for the Chef deployment scripts.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant. Will need to be updated to use Ansible's native testing frameworks.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Will need to be converted to Ansible test format.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need to be converted to Ansible test format.
- `chef-and-ansible/index.html`: Sample HTML file used by the website playbook. Can be reused as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml for testing)
- **Virtual Machine Technology**: Vagrant (used for testing in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **InSpec (latest)**: Replace with Ansible's native testing capabilities or integrate with Molecule for testing
- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management solution

### Security Considerations

- **SSL Configuration**: The `poodle_fix.yml` playbook addresses SSL vulnerabilities by enforcing TLSv1.2. This security practice should be maintained in the migrated solution.
- **Self-signed Certificates**: The `website_https.yml` playbook generates self-signed certificates. Consider using Let's Encrypt for production environments.
- **Vault/secrets management**: 
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - These should be moved to Ansible Vault or another secure secrets management solution

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks may require additional expertise in both technologies.
  - Mitigation: Use Ansible's assert module or Molecule for testing, or maintain InSpec as a testing tool if already established in the workflow.

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality.
  - Mitigation: Evaluate Ansible AWX/Tower as a replacement for Chef Server's functionality or use GitOps approaches with Ansible.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible) - Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already in Ansible) - Review and optimize the existing Ansible playbook
3. **InSpec Tests** (moderate complexity) - Convert to Ansible-compatible testing framework
4. **Chef Deployment Scripts** (high complexity) - Create Ansible roles to replace Chef Automate and Chef Server deployment

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes, not production deployment.
2. The InSpec tests are essential to the workflow and need to be preserved in some form.
3. There is a requirement to replace the Chef Server and Automate deployment with an Ansible-based solution.
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives.
6. The self-signed certificates in the website_https.yml playbook are acceptable for the use case, but may need to be replaced with proper certificates in production.