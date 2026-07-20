# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-based workflow. Estimated timeline: 1-2 weeks.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration considerations: Already in Ansible format, can be used as-is with minor adjustments.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Migration considerations: Already in Ansible format, can be used as-is.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations: Replace with Ansible Molecule or maintain as-is for testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration considerations: Can be maintained as-is or converted to Ansible assert tasks.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH compliance. Migration considerations: Can be maintained as-is or converted to Ansible assert tasks.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration considerations: Replace with Ansible playbook for infrastructure management.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Replace with Ansible playbook for infrastructure management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management or consider alternative compliance solutions like OpenSCAP or Ansible's built-in compliance capabilities
- **Chef InSpec**: Options include:
  1. Keep InSpec as a compliance tool and integrate with Ansible workflows
  2. Replace with Ansible's built-in testing capabilities
  3. Use alternative compliance tools like OpenSCAP with Ansible integration

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening implemented in poodle_fix.yml
- **SSH Hardening**: The SSH compliance profile in ssh_profile.rb needs to be maintained or converted to Ansible security tasks
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain

### Technical Challenges

- **Compliance Testing Integration**: Determining the best approach for integrating compliance testing with Ansible (keep InSpec or migrate to native Ansible testing)
  - Mitigation: Create a proof-of-concept for both approaches and evaluate based on team expertise and requirements
  
- **Infrastructure Deployment**: Replacing Chef Automate and Chef Infra Server deployment with equivalent infrastructure
  - Mitigation: Evaluate if Chef Automate/Infra Server is still needed or if Ansible can completely replace it

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Ensure idempotence and best practices

2. **Compliance Testing** (Moderate complexity)
   - Decide on compliance testing strategy (keep InSpec or migrate)
   - Implement chosen approach

3. **Infrastructure Deployment** (High complexity)
   - Replace Chef Automate and Chef Infra Server deployment scripts with Ansible playbooks
   - Implement secrets management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. There are no additional Chef cookbooks or recipes beyond what's visible in the repository
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. The team has expertise in both Chef and Ansible
7. The migration goal is to consolidate on Ansible while maintaining compliance capabilities