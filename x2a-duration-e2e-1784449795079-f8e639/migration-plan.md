# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations with a focus on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for verification
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS support, creates self-signed certificates, and deploys a simple website. Migration considerations include preserving the SSL configuration and certificate generation.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2. Migration considerations include ensuring this security hardening is maintained.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with an Ansible-native testing framework or adapting to use Molecule.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test that verifies HTTPS functionality and SSL security. Migration considerations include converting to Ansible test framework or maintaining InSpec as a testing tool.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec as a testing tool.
  
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for deploying alternative compliance platforms.
  
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for deploying alternative configuration management platforms.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a standalone testing tool integrated with Ansible workflows
- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing
- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX for orchestration and compliance reporting

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2 as implemented in poodle_fix.yml
- **Self-signed Certificates**: The current implementation generates self-signed certificates; consider using Let's Encrypt or other trusted certificate providers in the Ansible migration
- **SSH Security**: Maintain the SSH security controls verified by the InSpec profile
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL/TLS certificate references in Apache configuration
  - Count: 2 credential patterns detected in setup-automate scripts

### Technical Challenges

- **Compliance Testing**: Determining whether to maintain InSpec as a testing tool or migrate to Ansible-native testing solutions. InSpec provides specialized compliance testing capabilities that may be difficult to replicate with Ansible alone.
  - Mitigation: Consider using Ansible to invoke InSpec tests or explore Ansible Lint with custom rules for compliance checks.

- **Chef Automate Replacement**: Identifying an appropriate Ansible-based solution to replace Chef Automate's compliance reporting capabilities.
  - Mitigation: Evaluate Ansible Tower/AWX with compliance reporting plugins or integrate with third-party compliance tools.

### Migration Order

1. **chef-and-ansible/website_https.yml** (low risk, already in Ansible format)
2. **chef-and-ansible/poodle_fix.yml** (low risk, already in Ansible format)
3. **chef-and-ansible/tests** (moderate complexity, requires decision on testing strategy)
4. **setup-automate scripts** (high complexity, requires architectural decisions on replacement for Chef Automate/Infra Server)

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining the compliance testing capabilities currently provided by InSpec.
2. The current implementation is a demonstration/example rather than a production deployment, as indicated by the README.md.
3. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The migration will need to address both the infrastructure provisioning (currently split between Ansible and shell scripts) and the compliance testing (currently using InSpec).
6. The self-signed certificates in the current implementation may need to be replaced with a more robust certificate management solution.
7. The simple "Hello World" website is a placeholder and not a production application.