# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be standardized and integrated into a unified Ansible framework

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer, primarily due to the limited number of components and straightforward functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **ansible-apache-https**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **inspec-compliance-testing**:
    - Description: Chef InSpec tests for verifying HTTPS website and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website deployment
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server

### Target Details

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Migrate to Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use ansible-test framework
  - Option 3: Maintain InSpec as a testing tool but invoke it through Ansible

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening implemented in poodle_fix.yml
  - Approach: Create an Ansible role for Apache SSL hardening that enforces TLSv1.2
  
- **SSH Hardening**: The SSH security profile in ssh_profile.rb must be implemented in Ansible
  - Approach: Create an Ansible role that configures SSH with PermitRootLogin set to "no"

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment to Ansible requires understanding the specific requirements and dependencies
  - Mitigation: Create an Ansible role that handles the prerequisites and installation steps for Chef Automate

- **InSpec Testing Integration**: Maintaining compliance testing while migrating to Ansible
  - Mitigation: Either convert InSpec tests to Ansible assertions or create an Ansible role that installs and runs InSpec tests

### Migration Order

1. **ansible-apache-https** (low risk, already in Ansible)
   - Standardize the playbook structure
   - Add proper documentation
   - Implement idempotency improvements

2. **inspec-compliance-testing** (medium complexity)
   - Decide on testing strategy (convert to Ansible or keep InSpec)
   - Create integration points with Ansible playbooks

3. **chef-automate-deployment** (highest complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement secure credential management with Ansible Vault
   - Add proper error handling and idempotency

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "working examples" related to content created by Technical Product Marketing.

2. The Chef InSpec tests are intended to demonstrate compliance automation alongside Ansible rather than being a critical production component.

3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in a production environment.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.

5. The migration goal is to standardize on Ansible while maintaining the compliance testing capabilities currently provided by InSpec.

6. There are no external dependencies or integrations beyond what is visible in the repository.