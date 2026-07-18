# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with InSpec testing
3. InSpec compliance profiles for security validation

The migration complexity is relatively low as most of the Ansible components are already in place. The main focus will be on replacing the Chef server deployment scripts with Ansible equivalents and ensuring the InSpec testing framework continues to function within an Ansible-only workflow.

Estimated timeline: 1-2 weeks for a complete migration, with minimal disruption to existing operations.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec testing
    - Path: chef-and-ansible (VERIFIED)
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate (VERIFIED)
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations include ensuring this security fix is incorporated into the main playbook.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include updating the testing framework to work with the consolidated Ansible approach.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include preserving these tests for the Ansible-only workflow.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include integrating this into the Ansible-based compliance testing workflow.
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing this with an Ansible playbook for infrastructure deployment.
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing this with an Ansible playbook for infrastructure deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Retain as a compliance testing tool but integrate with Ansible workflow using the `ansible_inspec` module or by calling InSpec directly from Ansible tasks
- **Test Kitchen**: Replace with Ansible-native testing frameworks like Molecule, or adapt Test Kitchen to work with Ansible-only configurations
- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX for centralized management or use alternative compliance platforms that integrate with Ansible

### Security Considerations

- **SSL Configuration**: The existing playbooks enforce TLSv1.2 and disable insecure protocols. This security practice should be maintained in the migrated Ansible playbooks.
- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Ensure this security check is maintained and enforced in the Ansible configuration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely in the Ansible workflow
  - Count of credentials detected: 3 (username, password, organization name in deployment scripts)

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to function properly with the Ansible-only workflow. Mitigation: Use Ansible's `command` or `shell` modules to execute InSpec tests or investigate Ansible collections that provide InSpec integration.
  
- **Chef Server Replacement**: Determining if Chef Automate/Server functionality needs to be replaced with equivalent Ansible tooling. Mitigation: Evaluate requirements for centralized management and compliance reporting to determine if Ansible Tower/AWX is needed.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible directory): Low risk as these are already Ansible playbooks. Consolidate website_https.yml and poodle_fix.yml into a single playbook with proper role structure.
  
2. **InSpec Tests** (chef-and-ansible/tests): Moderate complexity. Adapt the existing InSpec tests to work with the new Ansible-only workflow, ensuring they can be executed as part of the Ansible deployment process.
  
3. **Chef Server Deployment** (setup-automate): High complexity. Replace the Chef server deployment scripts with equivalent Ansible playbooks, considering whether Chef Automate/Server functionality needs to be replaced with Ansible Tower/AWX.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, rather than being a production deployment.
  
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment rather than production infrastructure.
  
3. The InSpec tests are intended to be preserved as they provide valuable compliance checks, even in an Ansible-only workflow.
  
4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
  
5. There is no existing Ansible inventory or host configuration beyond what's specified in the kitchen.yml file.
  
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.