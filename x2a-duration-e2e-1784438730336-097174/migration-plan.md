# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations with a focus on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an Apache HTTPS website with self-signed certificates. Migration considerations include preserving the SSL configuration and virtual host setup.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration against POODLE vulnerability. Migration considerations include ensuring the security fix is maintained.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing framework or adapting to use Molecule.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec for compliance testing.
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for deployment of alternative compliance platforms.
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for deployment of alternative configuration management platforms.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a standalone compliance tool integrated with Ansible
- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for infrastructure management and compliance reporting

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening against POODLE vulnerability
- **Self-signed Certificates**: The certificate generation process should be preserved in Ansible
- **SSH Hardening**: The SSH security controls tested by InSpec should be implemented in Ansible
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password variables)
  - SSL certificates and keys generated and stored in `/etc/apache2/certs/`
  - No evidence of external secret management systems

### Technical Challenges

- **Compliance Testing**: Deciding whether to maintain InSpec for compliance testing or migrate to Ansible-native testing solutions. InSpec provides robust compliance testing capabilities that may be challenging to replicate with Ansible alone.
  - Mitigation: Consider using Ansible to deploy and run InSpec tests, preserving the compliance testing capabilities while standardizing on Ansible for infrastructure management.

- **Test Framework Migration**: Converting Test Kitchen workflow to Molecule or another Ansible-native testing framework.
  - Mitigation: Create equivalent Molecule scenarios that replicate the Test Kitchen functionality, ensuring test coverage is maintained.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **Testing Framework** (Moderate complexity)
   - Convert Test Kitchen configuration to Molecule or integrate InSpec with Ansible testing workflow

3. **Chef Deployment Scripts** (High complexity)
   - Replace Chef Automate/Infra Server deployment scripts with Ansible roles for deploying alternative solutions (AWX/Tower)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec compliance testing with Ansible, not to provide production-ready infrastructure code.

2. The InSpec tests are considered valuable and should be preserved in some form, either by maintaining InSpec as a compliance tool or by converting the tests to equivalent Ansible checks.

3. The Chef Automate and Chef Infra Server deployment scripts are intended for demonstration purposes and can be replaced with equivalent Ansible roles for deploying alternative solutions.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to cloud environments.

5. There is no external secret management system in use, and credentials are currently hardcoded in scripts.

6. The SSL configuration and security hardening are critical aspects that must be maintained in the migrated solution.