# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance verification

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer, as the repository primarily contains deployment scripts and simple Ansible playbooks rather than complex Chef cookbooks.

## Module Migration Plan

This repository contains shell scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with SSL/TLS configuration and InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, POODLE vulnerability mitigation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should maintain testing capabilities using Ansible Molecule or similar.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be preserved and enhanced in the migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for mitigating POODLE vulnerability. Can be preserved and enhanced in the migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS configuration. Can be preserved for compliance testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for Chef Automate deployment or consider if Chef Automate is still needed
- **Chef InSpec**: Maintain as a compliance testing tool alongside Ansible (no direct replacement needed)
- **Test Kitchen with Ansible**: Replace with Ansible Molecule for testing Ansible playbooks

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable SSLv3 to mitigate POODLE vulnerability. Migration should maintain or enhance these security controls.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password, email)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible requires understanding of Chef Automate's deployment requirements and system configurations.
  - Mitigation: Create an Ansible role that handles the same system configurations and deployment steps.
  
- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible.
  - Mitigation: Use Ansible's `shell` or `command` modules to execute InSpec tests as part of playbook execution, or integrate with CI/CD pipeline.

### Migration Order

1. **chef-and-ansible Ansible Playbooks** (Low risk, already in Ansible format)
   - Enhance existing playbooks with best practices
   - Update testing framework from Test Kitchen to Molecule
   
2. **setup-automate Bash Scripts** (Medium complexity)
   - Convert to Ansible playbooks
   - Implement secrets management with Ansible Vault
   - Add idempotency checks

### Assumptions

1. The repository is primarily used for demonstration and educational purposes rather than production deployments, based on the README description.
2. Chef InSpec is still desired as a compliance testing tool even after migration to pure Ansible.
3. The hardcoded credentials in the deployment scripts are examples and not actual production credentials.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The Apache configuration is a simple example and may need enhancement for production use.
6. The repository does not contain actual Chef cookbooks or complex Chef code, making the migration relatively straightforward.
7. Users of this repository have basic knowledge of both Chef and Ansible concepts.